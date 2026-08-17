# ============================================================================
# DRILLING PROGRAM & PROCEDURE GENERATOR - PROFESSIONAL EDITION
# Version 3.1 (Integrated Edition)
# Based on: Shell DEP, BP GP, Saudi Aramco SAES, IADC, API Standards
# ============================================================================
# File: main.py (Part 1 of 5)
# Core Application, GUI, Data Models
# ============================================================================

import sys
import os
import json
import math
import copy
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum, auto
from pathlib import Path
            
# PySide6 Imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QGroupBox, QFormLayout, QLabel, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QToolBar, QStatusBar, QMenuBar, QMenu, QFileDialog,
    QMessageBox, QProgressBar, QSplitter, QScrollArea, QFrame,
    QCheckBox, QRadioButton, QButtonGroup, QDateEdit, QTimeEdit,
    QHeaderView, QAbstractItemView, QDialog, QDialogButtonBox,
    QTreeWidget, QTreeWidgetItem, QStackedWidget, QGridLayout,
    QSizePolicy, QPlainTextEdit, QListWidget, QListWidgetItem, QInputDialog
)
from PySide6.QtCore import (
    Qt, QSize, Signal, Slot, QThread, QTimer, QSettings, QDate
)
from PySide6.QtGui import (
    QAction, QIcon, QFont, QColor, QPalette, QPixmap, QIntValidator,
    QDoubleValidator, QPainter, QBrush, QPen, QLinearGradient
)

from operational_templates import (
    TemplateLibrary, ParameterResolver, TemplateCategory,
    list_available_templates, list_available_phases
)

# Integrated tabs & tools (dashboard, risk analyzer, master programs, engineering)
from integrations import (
    DashboardTab, RiskAnalyzerTab, EngineeringToolsTab, DocumentPreviewDialog
)

# Cost Breakdown Structure (CBS) — editable price catalog & AFE
from cbs_ui import CostPricingTab

# Universal program & procedure generator wizard
from wizard_engine import GeneratorWizard, run_wizard

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('drilling_program.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DrillingProgram')


# ============================================================================
# ENUMERATIONS
# ============================================================================

class WellType(Enum):
    EXPLORATION = "Exploration"
    APPRAISAL = "Appraisal"
    DEVELOPMENT = "Development"
    INJECTION = "Injection"
    OBSERVATION = "Observation"
    WORKOVER = "Workover"
    SIDETRACK = "Sidetrack"


class WellProfile(Enum):
    VERTICAL = "Vertical"
    DIRECTIONAL_J = "Directional J-Type"
    DIRECTIONAL_S = "Directional S-Type"
    HORIZONTAL = "Horizontal"
    EXTENDED_REACH = "Extended Reach (ERD)"
    MULTILATERAL = "Multilateral"


class HoleSection(Enum):
    CONDUCTOR = "Conductor"
    SURFACE = "Surface"
    INTERMEDIATE = "Intermediate"
    PRODUCTION = "Production"
    LINER = "Liner"
    OPEN_HOLE = "Open Hole"


class MudType(Enum):
    WBM_BENTONITE = "WBM - Bentonite"
    WBM_POLYMER = "WBM - Polymer"
    WBM_KCL_POLYMER = "WBM - KCl Polymer"
    WBM_LIME = "WBM - Lime"
    WBM_SILICATE = "WBM - Silicate"
    OBM_DIESEL = "OBM - Diesel Based"
    OBM_MINERAL = "OBM - Mineral Oil Based"
    SBM = "SBM - Synthetic Based"
    FOAM = "Foam"
    AIR = "Air"
    BRINE_NACL = "Brine - NaCl"
    BRINE_CACL2 = "Brine - CaCl2"
    BRINE_CABR2 = "Brine - CaBr2"
    BRINE_ZN = "Brine - Zinc Bromide"


class CasingGrade(Enum):
    H40 = "H-40"
    J55 = "J-55"
    K55 = "K-55"
    N80 = "N-80"
    L80 = "L-80"
    C90 = "C90"
    C95 = "C-95"
    T95 = "T-95"
    P110 = "P-110"
    Q125 = "Q-125"
    V150 = "V-150"


class CasingConnection(Enum):
    STC = "Short Thread & Coupled (STC)"
    LTC = "Long Thread & Coupled (LTC)"
    BTC = "Buttress Thread & Coupled (BTC)"
    VAM_TOP = "VAM TOP"
    VAM_21 = "VAM 21"
    VAM_EDGE = "VAM EDGE"
    VAM_SLIJ = "VAM SLIJ-II"
    HUNTING_SEAL = "Hunting SEAL-LOCK"
    TENARIS_BLUE = "Tenaris Blue"
    TENARIS_DOPELESS = "Tenaris Dopeless"
    TSH_BLUE = "TSH Blue"
    FOX = "FOX"
    BEAR = "BEAR"
    TCS = "TCS"


class CementType(Enum):
    CLASS_A = "API Class A"
    CLASS_B = "API Class B"
    CLASS_C = "API Class C"
    CLASS_G = "API Class G"
    CLASS_H = "API Class H"
    MICRO_CEMENT = "Micro Cement"
    FOAM_CEMENT = "Foam Cement"


class BOPType(Enum):
    ANNULAR = "Annular Preventer"
    SINGLE_RAM = "Single Ram"
    DOUBLE_RAM = "Double Ram"
    TRIPLE_RAM = "Triple Ram"
    QUAD_RAM = "Quad Ram"
    SUBSEA_STACK = "Subsea Stack"


class RigType(Enum):
    LAND = "Land Rig"
    JACKUP = "Jack-Up"
    SEMISUBMERSIBLE = "Semi-Submersible"
    DRILLSHIP = "Drillship"
    PLATFORM = "Platform Rig"
    BARGE = "Barge Rig"
    COILED_TUBING = "Coiled Tubing Unit"


class BitType(Enum):
    PDC = "PDC"
    TRICONE_INSERT = "Tricone Insert"
    TRICONE_MILLED = "Tricone Milled Tooth"
    DIAMOND_NATURAL = "Natural Diamond"
    DIAMOND_IMPREG = "Impregnated Diamond"
    HYBRID = "Hybrid (Kymera)"
    BICENTER = "Bi-Center"
    CORING = "Coring Bit"
    HOLE_OPENER = "Hole Opener"


class FormationTopType(Enum):
    SAND = "Sand"
    SANDSTONE = "Sandstone"
    SHALE = "Shale"
    LIMESTONE = "Limestone"
    DOLOMITE = "Dolomite"
    MARL = "Marl"
    CLAY = "Clay"
    SALT = "Salt"
    ANHYDRITE = "Anhydrite"
    GYPSUM = "Gypsum"
    BASALT = "Basalt"
    GRANITE = "Granite"
    CONGLOMERATE = "Conglomerate"
    COAL = "Coal"
    CHALK = "Chalk"


class HazardType(Enum):
    LOST_CIRCULATION = "Lost Circulation"
    KICK = "Kick / Well Control"
    H2S = "H2S Gas"
    HIGH_PRESSURE = "Abnormal High Pressure"
    LOW_PRESSURE = "Sub-Normal Pressure"
    STUCK_PIPE = "Stuck Pipe"
    TIGHT_HOLE = "Tight Hole"
    SLOUGHING_SHALE = "Sloughing Shale"
    SALT_SECTION = "Salt Section"
    SHALLOW_GAS = "Shallow Gas"
    WATER_FLOW = "Shallow Water Flow"
    FAULT_ZONE = "Fault Zone"
    UNCONSOLIDATED = "Unconsolidated Formation"
    HIGH_TEMPERATURE = "High Temperature (>150°C)"
    CO2_CORROSION = "CO2 Corrosion"
    COLLISION_RISK = "Anti-Collision Risk"
    RUBBLE_ZONE = "Rubble Zone"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class CompanyInfo:
    """شرکت اپراتور و پیمانکار"""
    operator_name: str = ""
    operator_logo_path: str = ""
    contractor_name: str = ""
    contractor_logo_path: str = ""
    field_name: str = ""
    well_name: str = ""
    well_number: str = ""
    pad_name: str = ""
    rig_name: str = ""
    rig_type: str = RigType.LAND.value
    country: str = ""
    region: str = ""
    block_license: str = ""
    api_number: str = ""
    spud_date: str = ""
    prepared_by: str = ""
    reviewed_by: str = ""
    approved_by: str = ""
    revision: str = "0"
    document_number: str = ""
    classification: str = "Confidential"


@dataclass
class WellGeneralInfo:
    """اطلاعات عمومی چاه"""
    well_type: str = WellType.DEVELOPMENT.value
    well_profile: str = WellProfile.DIRECTIONAL_J.value
    total_depth_md: float = 0.0
    total_depth_tvd: float = 0.0
    water_depth: float = 0.0
    air_gap: float = 0.0
    ground_elevation: float = 0.0
    kb_elevation: float = 0.0
    rt_elevation: float = 0.0
    magnetic_declination: float = 0.0
    grid_convergence: float = 0.0
    surface_latitude: str = ""
    surface_longitude: str = ""
    target_latitude: str = ""
    target_longitude: str = ""
    coordinate_system: str = "WGS 84"
    seismic_reference: str = ""
    wellhead_type: str = ""
    xmas_tree_type: str = ""
    target_formation: str = ""
    target_zone: str = ""
    expected_reservoir_pressure: float = 0.0
    expected_reservoir_temperature: float = 0.0
    expected_h2s_concentration: float = 0.0
    expected_co2_concentration: float = 0.0
    nace_required: bool = False


@dataclass
class FormationTop:
    """اطلاعات سازند"""
    name: str = ""
    formation_type: str = FormationTopType.SANDSTONE.value
    md_top: float = 0.0
    md_bottom: float = 0.0
    tvd_top: float = 0.0
    tvd_bottom: float = 0.0
    pore_pressure_top: float = 0.0  # ppg EMW
    pore_pressure_bottom: float = 0.0
    fracture_gradient_top: float = 0.0
    fracture_gradient_bottom: float = 0.0
    overburden_gradient: float = 0.0
    temperature_top: float = 0.0  # °F or °C
    temperature_bottom: float = 0.0
    drillability: str = "Medium"  # Easy, Medium, Hard, Very Hard
    directional_tendency: str = "Neutral"
    remarks: str = ""


@dataclass
class HazardEntry:
    """ورودی خطرات"""
    hazard_type: str = HazardType.LOST_CIRCULATION.value
    md_top: float = 0.0
    md_bottom: float = 0.0
    severity: str = "Medium"  # Low, Medium, High, Critical
    probability: str = "Possible"  # Unlikely, Possible, Likely, Almost Certain
    description: str = ""
    mitigation: str = ""
    contingency: str = ""
    reference_well: str = ""


@dataclass
class CasingDesign:
    """طراحی لوله جداری"""
    section_name: str = ""
    section_type: str = HoleSection.SURFACE.value
    hole_size: float = 0.0  # inches
    casing_od: float = 0.0  # inches
    casing_id: float = 0.0  # inches
    casing_weight: float = 0.0  # ppf
    casing_grade: str = CasingGrade.N80.value
    casing_connection: str = CasingConnection.BTC.value
    setting_depth_md: float = 0.0
    setting_depth_tvd: float = 0.0
    shoe_depth_md: float = 0.0
    shoe_depth_tvd: float = 0.0
    top_of_cement_md: float = 0.0
    top_of_cement_tvd: float = 0.0
    cement_to_surface: bool = False
    liner_overlap: float = 0.0
    liner_top_md: float = 0.0
    burst_rating: float = 0.0  # psi
    collapse_rating: float = 0.0  # psi
    tensile_rating: float = 0.0  # lbs
    drift_id: float = 0.0  # inches
    min_design_factor_burst: float = 1.10
    min_design_factor_collapse: float = 1.10
    min_design_factor_tension: float = 1.60
    centralizer_spacing: float = 0.0  # ft
    centralizer_type: str = "Bow-Spring"
    float_collar_depth: float = 0.0
    float_shoe_type: str = "Float Shoe"
    number_of_joints: int = 0
    scratchers: bool = False
    is_liner: bool = False
    casing_accessories: str = ""
    remarks: str = ""


@dataclass
class CementDesign:
    """طراحی سیمانکاری"""
    section_name: str = ""
    casing_od: float = 0.0
    hole_size: float = 0.0
    shoe_depth_md: float = 0.0
    toc_md: float = 0.0
    lead_slurry_type: str = CementType.CLASS_G.value
    lead_slurry_density: float = 0.0  # ppg
    lead_slurry_yield: float = 0.0  # cu ft/sk
    lead_slurry_volume: float = 0.0  # bbls
    lead_slurry_thickening_time: float = 0.0  # hours
    lead_slurry_compressive_strength: float = 0.0  # psi @ 24hr
    tail_slurry_type: str = CementType.CLASS_G.value
    tail_slurry_density: float = 0.0
    tail_slurry_yield: float = 0.0
    tail_slurry_volume: float = 0.0
    tail_slurry_thickening_time: float = 0.0
    tail_slurry_compressive_strength: float = 0.0
    spacer_type: str = ""
    spacer_density: float = 0.0
    spacer_volume: float = 0.0
    wash_type: str = "Fresh Water"
    wash_volume: float = 0.0
    displacement_fluid: str = ""
    displacement_volume: float = 0.0
    displacement_rate: float = 0.0  # bpm
    max_ecd: float = 0.0
    pump_pressure_at_surface: float = 0.0
    excess_percentage: float = 50.0
    woc_time: float = 0.0  # hours
    plug_bump_pressure: float = 0.0  # psi
    cement_additives: str = ""
    stage_cementing: bool = False
    squeeze_required: bool = False
    cbl_cbil_required: bool = True
    remarks: str = ""


@dataclass
class DrillStringComponent:
    """اجزای رشته حفاری"""
    component_type: str = ""  # DP, HWDP, DC, Jar, Stabilizer, etc.
    od: float = 0.0
    id: float = 0.0
    weight: float = 0.0  # ppf
    length: float = 0.0  # ft
    grade: str = ""
    connection: str = ""
    tool_joint_od: float = 0.0
    tool_joint_id: float = 0.0
    makeup_torque: float = 0.0  # ft-lbs
    max_tensile: float = 0.0  # lbs
    fish_neck_od: float = 0.0
    serial_number: str = ""
    quantity: int = 1
    total_length: float = 0.0
    cumulative_length: float = 0.0
    remarks: str = ""


@dataclass
class BHADesign:
    """طراحی رشته ته چاهی"""
    section_name: str = ""
    hole_size: float = 0.0
    bha_number: int = 1
    bha_type: str = "Rotary"  # Rotary, Motor, RSS, Motor+RSS
    bit_type: str = BitType.PDC.value
    bit_size: float = 0.0
    bit_manufacturer: str = ""
    bit_model: str = ""
    bit_nozzles: str = ""  # e.g., "3x14, 2x13"
    bit_tfa: float = 0.0  # sq inches
    motor_type: str = ""
    motor_od: float = 0.0
    motor_bend: float = 0.0
    motor_lobe: str = ""  # e.g., "7/8"
    motor_flow_range: str = ""
    rss_type: str = ""
    rss_model: str = ""
    mwd_type: str = ""
    lwd_type: str = ""
    lwd_sensors: str = ""
    stabilizer_sizes: str = ""
    components: List[DrillStringComponent] = field(default_factory=list)
    total_length: float = 0.0
    total_weight: float = 0.0
    max_wob: float = 0.0  # klbs
    recommended_wob: str = ""  # e.g., "15-25 klbs"
    recommended_rpm: str = ""  # e.g., "120-180 RPM"
    recommended_flow_rate: str = ""  # e.g., "650-750 GPM"
    recommended_torque: str = ""
    remarks: str = ""


@dataclass
class MudProgram:
    """برنامه سیال حفاری"""
    section_name: str = ""
    hole_size: float = 0.0
    depth_from: float = 0.0
    depth_to: float = 0.0
    mud_type: str = MudType.WBM_KCL_POLYMER.value
    mud_weight_in: float = 0.0  # ppg
    mud_weight_out: float = 0.0
    funnel_viscosity: float = 0.0  # sec/qt
    plastic_viscosity: float = 0.0  # cP
    yield_point: float = 0.0  # lb/100sqft
    gel_strength_10s: float = 0.0
    gel_strength_10m: float = 0.0
    gel_strength_30m: float = 0.0
    fluid_loss: float = 0.0  # ml/30min
    hthp_fluid_loss: float = 0.0
    ph: float = 0.0
    chlorides: float = 0.0  # ppm
    calcium: float = 0.0  # ppm
    mbt: float = 0.0  # lb/bbl
    sand_content: float = 0.0  # %
    oil_water_ratio: str = ""  # for OBM/SBM
    electrical_stability: float = 0.0  # volts
    total_volume_required: float = 0.0  # bbls
    active_volume: float = 0.0
    reserve_volume: float = 0.0
    solids_control_equipment: str = ""
    key_additives: str = ""
    ecd_at_shoe: float = 0.0
    ecd_at_td: float = 0.0
    remarks: str = ""


@dataclass
class HydraulicsData:
    """داده‌های هیدرولیکی"""
    section_name: str = ""
    flow_rate: float = 0.0  # GPM
    spp: float = 0.0  # psi
    bit_pressure_drop: float = 0.0
    annular_pressure_loss: float = 0.0
    drillstring_pressure_loss: float = 0.0
    surface_equipment_loss: float = 0.0
    ecd_at_bit: float = 0.0
    ecd_at_shoe: float = 0.0
    annular_velocity_critical: float = 0.0  # ft/min
    jet_velocity: float = 0.0  # ft/s
    impact_force: float = 0.0  # lbs
    hsi: float = 0.0  # hp/sq.in
    swab_pressure: float = 0.0
    surge_pressure: float = 0.0
    max_trip_speed: float = 0.0  # ft/min
    cutting_transport_ratio: float = 0.0
    remarks: str = ""


@dataclass
class DirectionalPlan:
    """برنامه جهتی"""
    section_name: str = ""
    survey_tool: str = ""
    survey_frequency: float = 0.0  # every X ft
    kickoff_point_md: float = 0.0
    kickoff_point_tvd: float = 0.0
    build_rate: float = 0.0  # deg/100ft
    turn_rate: float = 0.0
    hold_inclination: float = 0.0
    hold_azimuth: float = 0.0
    target_inclination: float = 0.0
    target_azimuth: float = 0.0
    max_dls: float = 0.0  # deg/100ft
    horizontal_displacement: float = 0.0
    vertical_section: float = 0.0
    closure_distance: float = 0.0
    closure_direction: float = 0.0
    anti_collision_wells: str = ""
    wellpath_data: List[Dict] = field(default_factory=list)
    # Each entry: {md, tvd, inclination, azimuth, dls, ns, ew, vs, closure_dist, closure_dir}
    remarks: str = ""


@dataclass
class BOPStack:
    """مشخصات BOP"""
    bop_type: str = BOPType.TRIPLE_RAM.value
    working_pressure: float = 10000.0  # psi
    bore_size: float = 18.75  # inches
    manufacturer: str = ""
    model: str = ""
    serial_number: str = ""
    annular_preventer_size: float = 0.0
    annular_preventer_wp: float = 0.0
    pipe_ram_size: str = ""
    blind_ram: bool = True
    shear_ram: bool = True
    variable_bore_ram: bool = False
    casing_shear_ram: bool = False
    kill_line_size: float = 0.0
    choke_line_size: float = 0.0
    choke_manifold_wp: float = 0.0
    kill_manifold_wp: float = 0.0
    diverter_size: float = 0.0
    diverter_line_size: float = 0.0
    accumulator_capacity: float = 0.0  # gallons
    accumulator_precharge: float = 0.0  # psi
    function_test_frequency: str = "Weekly"
    pressure_test_frequency: str = "Per Section"
    bop_test_pressure_low: float = 250.0  # psi
    bop_test_pressure_high: float = 0.0  # psi (70% or 80% of WP)
    last_test_date: str = ""
    remarks: str = ""


@dataclass
class WellControlData:
    """داده‌های کنترل چاه"""
    maasp_surface: float = 0.0  # psi
    maasp_at_shoe: float = 0.0
    kick_tolerance: float = 0.0  # bbls
    kill_method: str = "Driller's Method"
    slow_pump_rate_1: float = 0.0  # spm
    slow_pump_pressure_1: float = 0.0  # psi
    slow_pump_rate_2: float = 0.0
    slow_pump_pressure_2: float = 0.0
    slow_pump_rate_3: float = 0.0
    slow_pump_pressure_3: float = 0.0
    pit_gain_action_level: float = 0.0  # bbls
    gas_detection_action_level: float = 0.0  # % or units
    h2s_action_levels: str = ""
    emergency_contacts: str = ""
    nearest_hospital: str = ""
    evacuation_route: str = ""
    remarks: str = ""


@dataclass
class EvaluationProgram:
    """برنامه ارزیابی"""
    section_name: str = ""
    logging_runs: List[Dict] = field(default_factory=list)
    # Each: {tool, interval_from, interval_to, provider, remarks}
    coring_program: List[Dict] = field(default_factory=list)
    # Each: {core_number, from_md, to_md, barrel_type, barrel_size, remarks}
    dst_program: List[Dict] = field(default_factory=list)
    # Each: {test_number, interval_from, interval_to, tool, remarks}
    mud_logging: str = ""
    formation_sampling: str = ""
    pressure_test_points: str = ""
    remarks: str = ""


@dataclass
class TimeEstimate:
    """تخمین زمان"""
    section_name: str = ""
    operation: str = ""
    depth_from: float = 0.0
    depth_to: float = 0.0
    estimated_days: float = 0.0
    rop_average: float = 0.0  # ft/hr
    trip_time: float = 0.0  # hrs
    connection_time: float = 0.0  # min/conn
    circulating_time: float = 0.0
    logging_time: float = 0.0
    casing_running_time: float = 0.0
    cementing_time: float = 0.0
    woc_time: float = 0.0
    nipple_up_down_time: float = 0.0
    flat_time: float = 0.0
    npt_contingency: float = 0.0  # %
    total_section_days: float = 0.0
    cumulative_days: float = 0.0
    remarks: str = ""


@dataclass
class RigSpecification:
    """مشخصات دکل"""
    rig_name: str = ""
    rig_type: str = RigType.LAND.value
    rig_contractor: str = ""
    max_hook_load: float = 0.0  # lbs
    max_rotary_torque: float = 0.0  # ft-lbs
    max_rotary_speed: float = 0.0  # RPM
    drawworks_power: float = 0.0  # HP
    mud_pump_1_type: str = ""
    mud_pump_1_hp: float = 0.0
    mud_pump_1_liner: float = 0.0
    mud_pump_1_max_pressure: float = 0.0
    mud_pump_1_max_flow: float = 0.0
    mud_pump_2_type: str = ""
    mud_pump_2_hp: float = 0.0
    mud_pump_2_liner: float = 0.0
    mud_pump_2_max_pressure: float = 0.0
    mud_pump_2_max_flow: float = 0.0
    mud_pump_3_type: str = ""
    mud_pump_3_hp: float = 0.0
    top_drive: bool = True
    top_drive_model: str = ""
    top_drive_torque: float = 0.0
    derrick_height: float = 0.0
    substructure_height: float = 0.0
    rotary_table_size: float = 0.0  # inches
    pit_volume_total: float = 0.0  # bbls
    pit_volume_active: float = 0.0
    shale_shaker_count: int = 0
    degasser_type: str = ""
    desander_desilter: str = ""
    centrifuge: str = ""
    generators: str = ""
    total_power: float = 0.0  # kW
    crane_capacity: float = 0.0  # tons
    accommodation: int = 0
    mast_capability: str = ""
    remarks: str = ""


@dataclass
class DrillingParameters:
    """پارامترهای حفاری هر سکشن"""
    section_name: str = ""
    hole_size: float = 0.0
    depth_from: float = 0.0
    depth_to: float = 0.0
    wob_min: float = 0.0
    wob_max: float = 0.0
    rpm_min: float = 0.0
    rpm_max: float = 0.0
    flow_rate_min: float = 0.0
    flow_rate_max: float = 0.0
    torque_max: float = 0.0
    rop_min: float = 0.0
    rop_max: float = 0.0
    rop_average: float = 0.0
    spp_max: float = 0.0
    overpull_limit: float = 0.0
    rotating_weight: float = 0.0
    pickup_weight: float = 0.0
    slackoff_weight: float = 0.0
    max_ecd: float = 0.0
    max_trip_speed_in: float = 0.0
    max_trip_speed_out: float = 0.0
    remarks: str = ""


@dataclass
class WellProject:
    """پروژه کامل چاه"""
    company_info: CompanyInfo = field(default_factory=CompanyInfo)
    well_info: WellGeneralInfo = field(default_factory=WellGeneralInfo)
    rig_spec: RigSpecification = field(default_factory=RigSpecification)
    formation_tops: List[FormationTop] = field(default_factory=list)
    hazards: List[HazardEntry] = field(default_factory=list)
    casing_design: List[CasingDesign] = field(default_factory=list)
    cement_design: List[CementDesign] = field(default_factory=list)
    bha_designs: List[BHADesign] = field(default_factory=list)
    mud_programs: List[MudProgram] = field(default_factory=list)
    hydraulics: List[HydraulicsData] = field(default_factory=list)
    directional_plan: DirectionalPlan = field(default_factory=DirectionalPlan)
    bop_stack: BOPStack = field(default_factory=BOPStack)
    well_control: WellControlData = field(default_factory=WellControlData)
    evaluation: EvaluationProgram = field(default_factory=EvaluationProgram)
    drilling_parameters: List[DrillingParameters] = field(default_factory=list)
    time_estimates: List[TimeEstimate] = field(default_factory=list)
    custom_procedures: Dict[str, str] = field(default_factory=dict)


# ============================================================================
# STYLE SHEET
# ============================================================================

DARK_STYLE = """
QMainWindow {
    background-color: #1a1a2e;
}
QWidget {
    background-color: #16213e;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}
QTabWidget::pane {
    border: 1px solid #0f3460;
    background-color: #16213e;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #1a1a2e;
    color: #a0a0a0;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: bold;
    min-width: 120px;
}
QTabBar::tab:selected {
    background-color: #0f3460;
    color: #e94560;
    border-bottom: 3px solid #e94560;
}
QTabBar::tab:hover {
    background-color: #0f3460;
    color: #ffffff;
}
QGroupBox {
    border: 2px solid #0f3460;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 20px;
    font-weight: bold;
    color: #e94560;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px;
    color: #e94560;
    font-size: 13px;
}
QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QDateEdit {
    background-color: #1a1a2e;
    border: 1px solid #0f3460;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e0e0e0;
    min-height: 28px;
}
QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {
    border: 2px solid #e94560;
    background-color: #16213e;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}
QComboBox QAbstractItemView {
    background-color: #1a1a2e;
    border: 1px solid #0f3460;
    color: #e0e0e0;
    selection-background-color: #e94560;
}
QPushButton {
    background-color: #0f3460;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
    font-weight: bold;
    font-size: 12px;
    min-height: 36px;
}
QPushButton:hover {
    background-color: #e94560;
}
QPushButton:pressed {
    background-color: #c73e54;
}
QPushButton#generateBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #e94560, stop:1 #0f3460);
    font-size: 16px;
    padding: 15px 40px;
    min-height: 50px;
    border-radius: 10px;
}
QPushButton#generateBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ff6b81, stop:1 #1a5276);
}
QTableWidget {
    background-color: #1a1a2e;
    gridline-color: #0f3460;
    border: 1px solid #0f3460;
    border-radius: 4px;
    color: #e0e0e0;
}
QTableWidget::item {
    padding: 5px;
}
QTableWidget::item:selected {
    background-color: #e94560;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #0f3460;
    color: #e94560;
    padding: 8px;
    border: 1px solid #1a1a2e;
    font-weight: bold;
}
QTextEdit, QPlainTextEdit {
    background-color: #1a1a2e;
    border: 1px solid #0f3460;
    border-radius: 4px;
    color: #e0e0e0;
    padding: 8px;
}
QScrollBar:vertical {
    background-color: #1a1a2e;
    width: 12px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background-color: #0f3460;
    border-radius: 6px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #e94560;
}
QScrollBar:horizontal {
    background-color: #1a1a2e;
    height: 12px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background-color: #0f3460;
    border-radius: 6px;
    min-width: 30px;
}
QProgressBar {
    border: 1px solid #0f3460;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    background-color: #1a1a2e;
    min-height: 24px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #e94560, stop:1 #0f3460);
    border-radius: 5px;
}
QStatusBar {
    background-color: #0f3460;
    color: #e0e0e0;
    font-size: 11px;
}
QMenuBar {
    background-color: #1a1a2e;
    color: #e0e0e0;
}
QMenuBar::item:selected {
    background-color: #e94560;
}
QMenu {
    background-color: #1a1a2e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
}
QMenu::item:selected {
    background-color: #e94560;
}
QToolBar {
    background-color: #1a1a2e;
    border-bottom: 2px solid #0f3460;
    spacing: 8px;
    padding: 4px;
}
QCheckBox {
    spacing: 8px;
    color: #e0e0e0;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #0f3460;
    border-radius: 4px;
    background-color: #1a1a2e;
}
QCheckBox::indicator:checked {
    background-color: #e94560;
    border-color: #e94560;
}
QLabel {
    color: #b0b0b0;
}
QLabel#sectionTitle {
    color: #e94560;
    font-size: 16px;
    font-weight: bold;
    padding: 10px 0;
}
QSplitter::handle {
    background-color: #0f3460;
    width: 3px;
}
QTreeWidget {
    background-color: #1a1a2e;
    border: 1px solid #0f3460;
    color: #e0e0e0;
}
QTreeWidget::item:selected {
    background-color: #e94560;
}
QListWidget {
    background-color: #1a1a2e;
    border: 1px solid #0f3460;
    color: #e0e0e0;
}
QListWidget::item:selected {
    background-color: #e94560;
}
QListWidget::item {
    padding: 6px;
    border-bottom: 1px solid #16213e;
}
QToolTip {
    background-color: #0f3460;
    color: #ffffff;
    border: 1px solid #e94560;
    padding: 6px;
    border-radius: 4px;
}
QPushButton:focus {
    border: 2px solid #e94560;
}
QLineEdit:disabled, QComboBox:disabled, QDoubleSpinBox:disabled,
QSpinBox:disabled, QTextEdit:disabled {
    background-color: #12122a;
    color: #606070;
}
QTableWidget QTableCornerButton::section {
    background-color: #0f3460;
}
QStatusBar::item {
    border: none;
}
"""


# ============================================================================
# HELPER WIDGETS
# ============================================================================

class SectionHeader(QLabel):
    """هدر سکشن"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("sectionTitle")
        self.setAlignment(Qt.AlignCenter)


class FormRow:
    """ردیف فرم ساده"""
    @staticmethod
    def add_line_edit(form_layout, label_text, placeholder="", tooltip=""):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        if tooltip:
            edit.setToolTip(tooltip)
        form_layout.addRow(label_text, edit)
        return edit

    @staticmethod
    def add_double_spin(form_layout, label_text, min_val=0.0, max_val=99999.0,
                        decimals=2, step=0.1, suffix="", tooltip=""):
        spin = QDoubleSpinBox()
        spin.setMinimum(min_val)
        spin.setMaximum(max_val)
        spin.setDecimals(decimals)
        spin.setSingleStep(step)
        if suffix:
            spin.setSuffix(f" {suffix}")
        if tooltip:
            spin.setToolTip(tooltip)
        form_layout.addRow(label_text, spin)
        return spin

    @staticmethod
    def add_spin(form_layout, label_text, min_val=0, max_val=99999,
                 suffix="", tooltip=""):
        spin = QSpinBox()
        spin.setMinimum(min_val)
        spin.setMaximum(max_val)
        if suffix:
            spin.setSuffix(f" {suffix}")
        if tooltip:
            spin.setToolTip(tooltip)
        form_layout.addRow(label_text, spin)
        return spin

    @staticmethod
    def add_combo(form_layout, label_text, items, tooltip=""):
        combo = QComboBox()
        if isinstance(items, type) and issubclass(items, Enum):
            for item in items:
                combo.addItem(item.value)
        else:
            combo.addItems(items)
        if tooltip:
            combo.setToolTip(tooltip)
        form_layout.addRow(label_text, combo)
        return combo

    @staticmethod
    def add_checkbox(form_layout, label_text, tooltip=""):
        cb = QCheckBox()
        if tooltip:
            cb.setToolTip(tooltip)
        form_layout.addRow(label_text, cb)
        return cb

    @staticmethod
    def add_text_edit(form_layout, label_text, height=80, tooltip=""):
        te = QTextEdit()
        te.setMaximumHeight(height)
        if tooltip:
            te.setToolTip(tooltip)
        form_layout.addRow(label_text, te)
        return te


# ============================================================================
# EDITABLE TABLE WIDGET
# ============================================================================

class EditableTable(QWidget):
    """جدول ویرایش‌پذیر با دکمه‌های اضافه/حذف"""
    dataChanged = Signal()
    
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.headers = headers
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        tb_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Add Row")
        self.btn_remove = QPushButton("➖ Remove Row")
        self.btn_clear = QPushButton("🗑 Clear All")
        self.btn_duplicate = QPushButton("📋 Duplicate")

        for btn in [self.btn_add, self.btn_remove, self.btn_duplicate, self.btn_clear]:
            btn.setMaximumHeight(32)
            btn.setMaximumWidth(140)
            tb_layout.addWidget(btn)

        tb_layout.addStretch()
        layout.addLayout(tb_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(200)

        # Smart column sizing based on column count
        if len(headers) <= 6:
            self.table.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)
        elif len(headers) <= 12:
            self.table.horizontalHeader().setSectionResizeMode(
                QHeaderView.Interactive)
            self.table.horizontalHeader().setMinimumSectionSize(80)
            self.table.horizontalHeader().setDefaultSectionSize(110)
            # Make last column stretch
            self.table.horizontalHeader().setStretchLastSection(True)
        else:
            # Many columns - use scroll
            self.table.horizontalHeader().setSectionResizeMode(
                QHeaderView.Interactive)
            self.table.horizontalHeader().setMinimumSectionSize(70)
            self.table.horizontalHeader().setDefaultSectionSize(95)
            self.table.horizontalHeader().setStretchLastSection(True)

        # Better header style
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #0f3460;
                color: #e94560;
                padding: 6px 4px;
                border: 1px solid #1a1a2e;
                font-weight: bold;
                font-size: 10px;
                min-height: 30px;
            }
        """)

        # Enable word wrap in headers
        self.table.horizontalHeader().setDefaultAlignment(
            Qt.AlignCenter | Qt.TextWordWrap)
        self.table.horizontalHeader().setFixedHeight(45)

        # Row height
        self.table.verticalHeader().setDefaultSectionSize(28)

        layout.addWidget(self.table)

        # Connections
        self.btn_add.clicked.connect(self.add_row)
        self.btn_remove.clicked.connect(self.remove_selected_row)
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_duplicate.clicked.connect(self.duplicate_row)
        self.table.cellChanged.connect(lambda: self.dataChanged.emit())
        
    def add_row(self, data=None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        if data:
            for col, val in enumerate(data):
                if col < len(self.headers):
                    self.table.setItem(row, col, QTableWidgetItem(str(val)))
        else:
            for col in range(len(self.headers)):
                self.table.setItem(row, col, QTableWidgetItem(""))
        self.dataChanged.emit()

    def remove_selected_row(self):
        rows = set()
        for item in self.table.selectedItems():
            rows.add(item.row())
        for row in sorted(rows, reverse=True):
            self.table.removeRow(row)
        self.dataChanged.emit()

    def clear_all(self):
        reply = QMessageBox.question(
            self, "Confirm", "Clear all rows?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.table.setRowCount(0)
            self.dataChanged.emit()

    def duplicate_row(self):
        current = self.table.currentRow()
        if current >= 0:
            data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(current, col)
                data.append(item.text() if item else "")
            self.add_row(data)

    def get_all_data(self):
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def set_data(self, data_list):
        self.table.setRowCount(0)
        for row_data in data_list:
            self.add_row(row_data)


# ============================================================================
# TAB: COMPANY & WELL INFORMATION
# ============================================================================

class CompanyWellTab(QScrollArea):
    """تب اطلاعات شرکت و چاه"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.fields = {}

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)

        # ---- Company Information ----
        grp_company = QGroupBox("Company Information")
        form_company = QFormLayout()
        form_company.setSpacing(8)

        self.fields['operator_name'] = FormRow.add_line_edit(
            form_company, "Operator Name:", "e.g., Saudi Aramco")
        self.fields['contractor_name'] = FormRow.add_line_edit(
            form_company, "Drilling Contractor:", "e.g., Nabors")
        self.fields['field_name'] = FormRow.add_line_edit(
            form_company, "Field Name:", "e.g., Ghawar")
        self.fields['well_name'] = FormRow.add_line_edit(
            form_company, "Well Name:", "e.g., GW-125")
        self.fields['well_number'] = FormRow.add_line_edit(
            form_company, "Well Number:", "e.g., 125")
        self.fields['pad_name'] = FormRow.add_line_edit(
            form_company, "Pad/Platform Name:")
        self.fields['rig_name'] = FormRow.add_line_edit(
            form_company, "Rig Name:", "e.g., Rig 45")
        self.fields['rig_type'] = FormRow.add_combo(
            form_company, "Rig Type:", RigType)
        self.fields['country'] = FormRow.add_line_edit(
            form_company, "Country:")
        self.fields['region'] = FormRow.add_line_edit(
            form_company, "Region/Area:")
        self.fields['block_license'] = FormRow.add_line_edit(
            form_company, "Block/License:")
        self.fields['api_number'] = FormRow.add_line_edit(
            form_company, "API/Well ID Number:")
        self.fields['document_number'] = FormRow.add_line_edit(
            form_company, "Document Number:", "e.g., DRL-PRG-2024-001")
        self.fields['revision'] = FormRow.add_line_edit(
            form_company, "Revision:", "0")
        self.fields['classification'] = FormRow.add_combo(
            form_company, "Classification:",
            ["Confidential", "Internal", "Restricted", "Public"])
        self.fields['prepared_by'] = FormRow.add_line_edit(
            form_company, "Prepared By:")
        self.fields['reviewed_by'] = FormRow.add_line_edit(
            form_company, "Reviewed By:")
        self.fields['approved_by'] = FormRow.add_line_edit(
            form_company, "Approved By:")

        # Spud Date
        spud_layout = QHBoxLayout()
        self.fields['spud_date'] = QDateEdit()
        self.fields['spud_date'].setCalendarPopup(True)
        self.fields['spud_date'].setDate(QDate.currentDate())
        spud_layout.addWidget(self.fields['spud_date'])
        form_company.addRow("Planned Spud Date:", spud_layout)

        grp_company.setLayout(form_company)
        main_layout.addWidget(grp_company)

        # ---- Well General Information ----
        grp_well = QGroupBox("Well General Information")
        form_well = QFormLayout()
        form_well.setSpacing(8)

        self.fields['well_type'] = FormRow.add_combo(
            form_well, "Well Type:", WellType)
        self.fields['well_profile'] = FormRow.add_combo(
            form_well, "Well Profile:", WellProfile)
        self.fields['total_depth_md'] = FormRow.add_double_spin(
            form_well, "Total Depth (MD):", 0, 50000, 1, 100, "ft",
            "Measured Depth to TD")
        self.fields['total_depth_tvd'] = FormRow.add_double_spin(
            form_well, "Total Depth (TVD):", 0, 50000, 1, 100, "ft",
            "True Vertical Depth to TD")
        self.fields['water_depth'] = FormRow.add_double_spin(
            form_well, "Water Depth:", 0, 15000, 1, 10, "ft")
        self.fields['air_gap'] = FormRow.add_double_spin(
            form_well, "Air Gap (RKB to MSL):", 0, 500, 1, 1, "ft")
        self.fields['ground_elevation'] = FormRow.add_double_spin(
            form_well, "Ground Elevation:", -500, 10000, 1, 1, "ft")
        self.fields['kb_elevation'] = FormRow.add_double_spin(
            form_well, "KB Elevation:", 0, 1000, 1, 1, "ft")

        grp_well.setLayout(form_well)
        main_layout.addWidget(grp_well)

        # ---- Location & Coordinates ----
        grp_loc = QGroupBox("Location & Coordinates")
        form_loc = QFormLayout()
        form_loc.setSpacing(8)

        self.fields['surface_latitude'] = FormRow.add_line_edit(
            form_loc, "Surface Latitude:", "e.g., 25° 15' 30.5\" N")
        self.fields['surface_longitude'] = FormRow.add_line_edit(
            form_loc, "Surface Longitude:", "e.g., 49° 45' 22.3\" E")
        self.fields['target_latitude'] = FormRow.add_line_edit(
            form_loc, "Target Latitude:")
        self.fields['target_longitude'] = FormRow.add_line_edit(
            form_loc, "Target Longitude:")
        self.fields['coordinate_system'] = FormRow.add_combo(
            form_loc, "Coordinate System:",
            ["WGS 84", "UTM Zone 38N", "UTM Zone 39N", "UTM Zone 40N",
             "ED50", "NAD27", "NAD83", "Local Grid"])
        self.fields['magnetic_declination'] = FormRow.add_double_spin(
            form_loc, "Magnetic Declination:", -30, 30, 2, 0.1, "°")
        self.fields['grid_convergence'] = FormRow.add_double_spin(
            form_loc, "Grid Convergence:", -10, 10, 2, 0.01, "°")

        grp_loc.setLayout(form_loc)
        main_layout.addWidget(grp_loc)

        # ---- Reservoir Information ----
        grp_res = QGroupBox("Target / Reservoir Information")
        form_res = QFormLayout()
        form_res.setSpacing(8)

        self.fields['target_formation'] = FormRow.add_line_edit(
            form_res, "Target Formation:", "e.g., Arab-D")
        self.fields['target_zone'] = FormRow.add_line_edit(
            form_res, "Target Zone:", "e.g., Zone 2B")
        self.fields['expected_reservoir_pressure'] = FormRow.add_double_spin(
            form_res, "Expected Reservoir Pressure:", 0, 30000, 0, 100, "psi")
        self.fields['expected_reservoir_temperature'] = FormRow.add_double_spin(
            form_res, "Expected Reservoir Temperature:", 0, 500, 0, 5, "°F")
        self.fields['expected_h2s'] = FormRow.add_double_spin(
            form_res, "Expected H₂S:", 0, 100, 1, 0.1, "%")
        self.fields['expected_co2'] = FormRow.add_double_spin(
            form_res, "Expected CO₂:", 0, 100, 1, 0.1, "%")
        self.fields['nace_required'] = FormRow.add_checkbox(
            form_res, "NACE MR-0175 Required:")

        # Wellhead & Tree
        self.fields['wellhead_type'] = FormRow.add_combo(
            form_res, "Wellhead Type:",
            ["Conventional", "Compact", "Mudline Suspension",
             "Subsea Wellhead", "Multi-Bowl"])
        self.fields['xmas_tree_type'] = FormRow.add_combo(
            form_res, "Christmas Tree Type:",
            ["Conventional", "Horizontal Tree", "Vertical Tree",
             "Subsea Horizontal", "Subsea Vertical", "N/A"])

        grp_res.setLayout(form_res)
        main_layout.addWidget(grp_res)

        # ---- Seismic Reference ----
        grp_seis = QGroupBox("Seismic & Geological Reference")
        form_seis = QFormLayout()
        self.fields['seismic_reference'] = FormRow.add_text_edit(
            form_seis, "Seismic Reference:", 60,
            "Reference seismic lines and interpretation")
        grp_seis.setLayout(form_seis)
        main_layout.addWidget(grp_seis)

        main_layout.addStretch()
        self.setWidget(container)

    def get_data(self) -> Tuple[CompanyInfo, WellGeneralInfo]:
        ci = CompanyInfo()
        ci.operator_name = self.fields['operator_name'].text()
        ci.contractor_name = self.fields['contractor_name'].text()
        ci.field_name = self.fields['field_name'].text()
        ci.well_name = self.fields['well_name'].text()
        ci.well_number = self.fields['well_number'].text()
        ci.pad_name = self.fields['pad_name'].text()
        ci.rig_name = self.fields['rig_name'].text()
        ci.rig_type = self.fields['rig_type'].currentText()
        ci.country = self.fields['country'].text()
        ci.region = self.fields['region'].text()
        ci.block_license = self.fields['block_license'].text()
        ci.api_number = self.fields['api_number'].text()
        ci.document_number = self.fields['document_number'].text()
        ci.revision = self.fields['revision'].text()
        ci.classification = self.fields['classification'].currentText()
        ci.prepared_by = self.fields['prepared_by'].text()
        ci.reviewed_by = self.fields['reviewed_by'].text()
        ci.approved_by = self.fields['approved_by'].text()
        ci.spud_date = self.fields['spud_date'].date().toString("yyyy-MM-dd")

        wi = WellGeneralInfo()
        wi.well_type = self.fields['well_type'].currentText()
        wi.well_profile = self.fields['well_profile'].currentText()
        wi.total_depth_md = self.fields['total_depth_md'].value()
        wi.total_depth_tvd = self.fields['total_depth_tvd'].value()
        wi.water_depth = self.fields['water_depth'].value()
        wi.air_gap = self.fields['air_gap'].value()
        wi.ground_elevation = self.fields['ground_elevation'].value()
        wi.kb_elevation = self.fields['kb_elevation'].value()
        wi.surface_latitude = self.fields['surface_latitude'].text()
        wi.surface_longitude = self.fields['surface_longitude'].text()
        wi.target_latitude = self.fields['target_latitude'].text()
        wi.target_longitude = self.fields['target_longitude'].text()
        wi.coordinate_system = self.fields['coordinate_system'].currentText()
        wi.magnetic_declination = self.fields['magnetic_declination'].value()
        wi.grid_convergence = self.fields['grid_convergence'].value()
        wi.target_formation = self.fields['target_formation'].text()
        wi.target_zone = self.fields['target_zone'].text()
        wi.expected_reservoir_pressure = self.fields[
            'expected_reservoir_pressure'].value()
        wi.expected_reservoir_temperature = self.fields[
            'expected_reservoir_temperature'].value()
        wi.expected_h2s_concentration = self.fields['expected_h2s'].value()
        wi.expected_co2_concentration = self.fields['expected_co2'].value()
        wi.nace_required = self.fields['nace_required'].isChecked()
        wi.wellhead_type = self.fields['wellhead_type'].currentText()
        wi.xmas_tree_type = self.fields['xmas_tree_type'].currentText()
        wi.seismic_reference = self.fields['seismic_reference'].toPlainText()

        return ci, wi


# ============================================================================
# TAB: FORMATION TOPS & HAZARDS
# ============================================================================

class FormationHazardTab(QScrollArea):
    """تب سازندها و خطرات"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)

        # ---- Formation Tops ----
        grp_form = QGroupBox("Formation Tops (Prognosis)")
        form_layout = QVBoxLayout()

        self.formation_table = EditableTable([
            "Formation Name", "Lithology", "MD Top (ft)", "MD Bottom (ft)",
            "TVD Top (ft)", "TVD Bottom (ft)", "Pore Pressure Top (ppg)",
            "Pore Pressure Bottom (ppg)", "Frac Gradient Top (ppg)",
            "Frac Gradient Bottom (ppg)", "Overburden (ppg)",
            "Temp Top (°F)", "Temp Bottom (°F)",
            "Drillability", "Directional Tendency", "Remarks"
        ])
        form_layout.addWidget(self.formation_table)

        # Add preset buttons
        preset_layout = QHBoxLayout()
        btn_preset_1 = QPushButton("📋 Load Sample (Middle East)")
        btn_preset_2 = QPushButton("📋 Load Sample (North Sea)")
        btn_preset_3 = QPushButton("📋 Load Sample (Gulf of Mexico)")
        btn_preset_1.clicked.connect(self.load_sample_me)
        btn_preset_2.clicked.connect(self.load_sample_ns)
        btn_preset_3.clicked.connect(self.load_sample_gom)
        preset_layout.addWidget(btn_preset_1)
        preset_layout.addWidget(btn_preset_2)
        preset_layout.addWidget(btn_preset_3)
        preset_layout.addStretch()
        form_layout.addLayout(preset_layout)

        grp_form.setLayout(form_layout)
        main_layout.addWidget(grp_form)

        # ---- Hazards ----
        grp_hazard = QGroupBox("Anticipated Hazards & Risks")
        hazard_layout = QVBoxLayout()

        self.hazard_table = EditableTable([
            "Hazard Type", "MD Top (ft)", "MD Bottom (ft)",
            "Severity", "Probability", "Description",
            "Mitigation Measures", "Contingency Plan",
            "Reference Well"
        ])
        hazard_layout.addWidget(self.hazard_table)

        grp_hazard.setLayout(hazard_layout)
        main_layout.addWidget(grp_hazard)

        # ---- Offset Wells ----
        grp_offset = QGroupBox("Offset Well Data Summary")
        offset_layout = QVBoxLayout()

        self.offset_table = EditableTable([
            "Well Name", "Distance (ft)", "TD (ft)", "Days to TD",
            "Well Type", "Key Observations", "NPT Events",
            "Lessons Learned"
        ])
        offset_layout.addWidget(self.offset_table)

        grp_offset.setLayout(offset_layout)
        main_layout.addWidget(grp_offset)

        main_layout.addStretch()
        self.setWidget(container)

    def load_sample_me(self):
        """نمونه داده خاورمیانه"""
        sample = [
            ["Dibdibba Fm", "Sand", "0", "500", "0", "500",
             "8.6", "8.6", "14.0", "14.5", "16.0",
             "100", "120", "Easy", "Neutral", "Unconsolidated"],
            ["Dammam Fm", "Limestone", "500", "1800", "500", "1800",
             "8.7", "8.8", "14.5", "15.0", "16.5",
             "120", "160", "Medium", "Neutral",
             "Possible lost circulation"],
            ["Rus Fm", "Anhydrite/Marl", "1800", "2500", "1800", "2500",
             "8.8", "9.0", "15.0", "15.5", "17.0",
             "160", "180", "Medium", "Neutral", ""],
            ["UER (Umm Er Radhuma)", "Limestone", "2500", "3500",
             "2500", "3500", "8.9", "9.2", "15.5", "16.0", "17.5",
             "180", "210", "Medium", "Build", "Lost circulation zone"],
            ["Aruma Fm", "Limestone", "3500", "5000", "3500", "5000",
             "9.0", "9.5", "16.0", "16.5", "18.0",
             "210", "240", "Hard", "Hold", ""],
            ["Wasia Fm", "Sandstone/Limestone", "5000", "6500",
             "5000", "6500", "9.2", "9.8", "16.5", "17.0", "18.5",
             "240", "270", "Medium", "Hold", ""],
            ["Shuaiba Fm", "Limestone", "6500", "7500", "6500", "7500",
             "9.5", "10.0", "17.0", "17.5", "19.0",
             "270", "290", "Hard", "Hold", "Dense limestone"],
            ["Biyadh Fm", "Sandstone", "7500", "8500", "7500", "8500",
             "10.0", "10.5", "17.5", "18.0", "19.5",
             "290", "310", "Medium", "Drop", ""],
            ["Arab-D", "Limestone/Dolomite", "8500", "9500",
             "8500", "9500", "10.2", "10.5", "17.0", "17.5", "19.0",
             "310", "340", "Hard", "Hold",
             "TARGET - Reservoir Zone"]
        ]
        self.formation_table.set_data(sample)

    def load_sample_ns(self):
        """نمونه داده دریای شمال"""
        sample = [
            ["Nordland Fm", "Clay/Sand", "0", "800", "0", "800",
             "8.6", "8.6", "13.0", "14.0", "15.5",
             "40", "60", "Easy", "Neutral", "Shallow gas risk"],
            ["Hordaland Fm", "Shale/Marl", "800", "3000", "800", "3000",
             "8.8", "9.5", "14.0", "16.0", "17.0",
             "60", "120", "Medium", "Neutral", "Reactive shales"],
            ["Rogaland Fm", "Shale/Limestone", "3000", "5000",
             "3000", "5000", "9.5", "12.0", "16.0", "17.5", "18.5",
             "120", "180", "Medium", "Build",
             "HPHT transition zone"],
            ["Shetland Fm", "Chalk/Marl", "5000", "8000",
             "5000", "8000", "12.0", "14.5", "17.5", "18.5", "20.0",
             "180", "260", "Hard", "Hold", "High pressure"],
            ["Brent Group", "Sandstone", "8000", "10000",
             "8000", "10000", "14.0", "15.5", "18.0", "19.0", "20.5",
             "260", "320", "Medium", "Hold",
             "TARGET - Reservoir"]
        ]
        self.formation_table.set_data(sample)

    def load_sample_gom(self):
        """نمونه داده خلیج مکزیک"""
        sample = [
            ["Recent Sediments", "Clay/Sand", "0", "2000", "0", "2000",
             "8.6", "8.7", "12.5", "14.0", "15.0",
             "60", "80", "Easy", "Neutral",
             "Shallow water flow risk"],
            ["Pliocene", "Shale/Sand", "2000", "6000", "2000", "6000",
             "8.7", "9.5", "14.0", "16.0", "17.0",
             "80", "150", "Medium", "Neutral",
             "Geopressure transition"],
            ["Miocene", "Sand/Shale", "6000", "12000", "6000", "12000",
             "9.5", "13.0", "16.0", "17.5", "19.0",
             "150", "250", "Medium", "Build",
             "Overpressured sands"],
            ["Lower Miocene", "Sandstone", "12000", "18000",
             "12000", "18000", "13.0", "16.0", "17.5", "18.5", "20.0",
             "250", "350", "Hard", "Hold",
             "TARGET - Deepwater reservoir"],
        ]
        self.formation_table.set_data(sample)

    def get_formation_data(self) -> List[FormationTop]:
        formations = []
        for row in self.formation_table.get_all_data():
            if row[0]:
                ft = FormationTop()
                ft.name = row[0]
                ft.formation_type = row[1]
                try:
                    ft.md_top = float(row[2]) if row[2] else 0
                    ft.md_bottom = float(row[3]) if row[3] else 0
                    ft.tvd_top = float(row[4]) if row[4] else 0
                    ft.tvd_bottom = float(row[5]) if row[5] else 0
                    ft.pore_pressure_top = float(row[6]) if row[6] else 0
                    ft.pore_pressure_bottom = float(row[7]) if row[7] else 0
                    ft.fracture_gradient_top = float(row[8]) if row[8] else 0
                    ft.fracture_gradient_bottom = float(row[9]) if row[9] else 0
                    ft.overburden_gradient = float(row[10]) if row[10] else 0
                    ft.temperature_top = float(row[11]) if row[11] else 0
                    ft.temperature_bottom = float(row[12]) if row[12] else 0
                except ValueError:
                    pass
                ft.drillability = row[13] if len(row) > 13 else ""
                ft.directional_tendency = row[14] if len(row) > 14 else ""
                ft.remarks = row[15] if len(row) > 15 else ""
                formations.append(ft)
        return formations

    def get_hazard_data(self) -> List[HazardEntry]:
        hazards = []
        for row in self.hazard_table.get_all_data():
            if row[0]:
                h = HazardEntry()
                h.hazard_type = row[0]
                try:
                    h.md_top = float(row[1]) if row[1] else 0
                    h.md_bottom = float(row[2]) if row[2] else 0
                except ValueError:
                    pass
                h.severity = row[3]
                h.probability = row[4]
                h.description = row[5]
                h.mitigation = row[6]
                h.contingency = row[7]
                h.reference_well = row[8] if len(row) > 8 else ""
                hazards.append(h)
        return hazards


# ============================================================================
# TAB: CASING DESIGN
# ============================================================================

class CasingDesignTab(QScrollArea):
    """تب طراحی لوله جداری"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)

        # ---- Casing Program Table ----
        grp_casing = QGroupBox("Casing Program")
        casing_layout = QVBoxLayout()

        self.casing_table = EditableTable([
            "Section Name", "Section Type", "Hole Size (in)",
            "Casing OD (in)", "Casing ID (in)", "Weight (ppf)",
            "Grade", "Connection", "Setting Depth MD (ft)",
            "Setting Depth TVD (ft)", "TOC MD (ft)",
            "Burst Rating (psi)", "Collapse Rating (psi)",
            "Tensile Rating (klbs)", "Drift ID (in)",
            "DF Burst", "DF Collapse", "DF Tension",
            "Centralizer Type", "Centralizer Spacing (ft)",
            "Float Collar Depth (ft)", "Is Liner",
            "Liner Overlap (ft)", "Remarks"
        ])
        casing_layout.addWidget(self.casing_table)

        # Sample Data Button
        btn_layout = QHBoxLayout()
        btn_sample = QPushButton("📋 Load Sample Casing Program")
        btn_sample.clicked.connect(self.load_sample)
        btn_layout.addWidget(btn_sample)
        btn_layout.addStretch()
        casing_layout.addLayout(btn_layout)

        grp_casing.setLayout(casing_layout)
        main_layout.addWidget(grp_casing)

        # ---- Casing Design Basis ----
        grp_basis = QGroupBox("Casing Design Basis & Assumptions")
        basis_layout = QFormLayout()

        self.fields = {}
        self.fields['design_method'] = FormRow.add_combo(
            basis_layout, "Design Method:",
            ["Deterministic (API RP 5C3)", "Load & Resistance Factor (ISO 10400)",
             "Probabilistic"])
        self.fields['burst_scenario'] = FormRow.add_combo(
            basis_layout, "Burst Design Scenario:",
            ["DST with Full Evacuation", "Gas Kick at Shoe",
             "Injection Down Casing", "Tubing Leak"])
        self.fields['collapse_scenario'] = FormRow.add_combo(
            basis_layout, "Collapse Design Scenario:",
            ["Full Evacuation", "Lost Returns + Gas Kick",
             "Cementing", "Above Cement Collapse"])
        self.fields['corrosion_allowance'] = FormRow.add_double_spin(
            basis_layout, "Corrosion Allowance:", 0, 0.5, 3, 0.01, "in")
        self.fields['wear_allowance'] = FormRow.add_double_spin(
            basis_layout, "Wear Allowance:", 0, 30, 0, 1, "%")
        self.fields['temperature_derating'] = FormRow.add_checkbox(
            basis_layout, "Temperature De-rating Applied:")
        self.fields['biaxial_check'] = FormRow.add_checkbox(
            basis_layout, "Biaxial (VME) Check:")
        self.fields['connection_check'] = FormRow.add_checkbox(
            basis_layout, "Connection Sealability Check:")
        self.fields['design_remarks'] = FormRow.add_text_edit(
            basis_layout, "Design Remarks:", 80)

        grp_basis.setLayout(basis_layout)
        main_layout.addWidget(grp_basis)

        main_layout.addStretch()
        self.setWidget(container)

    def load_sample(self):
        sample = [
            ["Conductor", "Conductor", "36", "30", "28.0", "309.72",
             "X-52", "Welded", "200", "200", "0",
             "2500", "1000", "500", "28.0",
             "1.10", "1.10", "1.60", "Rigid", "40", "180",
             "No", "0", "Driven/Cemented"],
            ["Surface", "Surface", "26", "20", "18.73", "133",
             "K-55", "BTC", "2000", "2000", "0",
             "3060", "1490", "1160", "18.63",
             "1.10", "1.10", "1.60", "Bow-Spring", "60",
             "1950", "No", "0", "Cement to Surface"],
            ["Intermediate", "Intermediate", "17-1/2", "13-3/8",
             "12.415", "72", "N-80", "BTC", "6500", "6500",
             "4000", "5020", "2670", "1556", "12.259",
             "1.10", "1.10", "1.60", "Bow-Spring", "60",
             "6440", "No", "0", ""],
            ["Production", "Production", "12-1/4", "9-5/8",
             "8.535", "53.5", "L-80", "VAM TOP", "9500",
             "9500", "5500", "7930", "4750", "1243",
             "8.379", "1.10", "1.10", "1.80",
             "Bow-Spring", "40", "9440", "No", "0",
             "NACE compliant"],
        ]
        self.casing_table.set_data(sample)

    def get_data(self) -> List[CasingDesign]:
        casings = []
        for row in self.casing_table.get_all_data():
            if row[0]:
                cd = CasingDesign()
                cd.section_name = row[0]
                cd.section_type = row[1]
                try:
                    cd.hole_size = float(row[2]) if row[2] else 0
                    cd.casing_od = float(row[3]) if row[3] else 0
                    cd.casing_id = float(row[4]) if row[4] else 0
                    cd.casing_weight = float(row[5]) if row[5] else 0
                except ValueError:
                    pass
                cd.casing_grade = row[6]
                cd.casing_connection = row[7]
                try:
                    cd.setting_depth_md = float(row[8]) if row[8] else 0
                    cd.setting_depth_tvd = float(row[9]) if row[9] else 0
                    cd.top_of_cement_md = float(row[10]) if row[10] else 0
                    cd.burst_rating = float(row[11]) if row[11] else 0
                    cd.collapse_rating = float(row[12]) if row[12] else 0
                    cd.tensile_rating = float(row[13]) if row[13] else 0
                    cd.drift_id = float(row[14]) if row[14] else 0
                    cd.min_design_factor_burst = float(row[15]) if row[15] else 1.1
                    cd.min_design_factor_collapse = float(row[16]) if row[16] else 1.1
                    cd.min_design_factor_tension = float(row[17]) if row[17] else 1.6
                except ValueError:
                    pass
                cd.centralizer_type = row[18] if len(row) > 18 else ""
                try:
                    cd.centralizer_spacing = float(row[19]) if row[19] else 0
                    cd.float_collar_depth = float(row[20]) if row[20] else 0
                except ValueError:
                    pass
                cd.is_liner = row[21].lower() == 'yes' if len(row) > 21 else False
                try:
                    cd.liner_overlap = float(row[22]) if row[22] else 0
                except ValueError:
                    pass
                cd.remarks = row[23] if len(row) > 23 else ""
                casings.append(cd)
        return casings


# ============================================================================
# TAB: MUD PROGRAM
# ============================================================================

class MudProgramTab(QScrollArea):
    """تب برنامه سیال حفاری"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)

        # ---- Mud Program ----
        grp_mud = QGroupBox("Drilling Fluid Program")
        mud_layout = QVBoxLayout()

        self.mud_table = EditableTable([
            "Section", "Hole Size (in)", "Depth From (ft)",
            "Depth To (ft)", "Mud Type", "MW In (ppg)",
            "MW Out (ppg)", "FV (sec/qt)", "PV (cP)",
            "YP (lb/100ft²)", "Gel 10s", "Gel 10m",
            "Gel 30m", "API FL (ml)", "HTHP FL (ml)",
            "pH", "Chlorides (ppm)", "MBT (lb/bbl)",
            "Sand (%)", "OWR", "ES (volts)",
            "Total Vol (bbl)", "Active Vol (bbl)",
            "Key Additives", "ECD at Shoe (ppg)",
            "ECD at TD (ppg)", "Remarks"
        ])
        mud_layout.addWidget(self.mud_table)

        btn_layout = QHBoxLayout()
        btn_sample = QPushButton("📋 Load Sample Mud Program")
        btn_sample.clicked.connect(self.load_sample)
        btn_layout.addWidget(btn_sample)
        btn_layout.addStretch()
        mud_layout.addLayout(btn_layout)

        grp_mud.setLayout(mud_layout)
        main_layout.addWidget(grp_mud)

        # ---- Solids Control ----
        grp_solids = QGroupBox("Solids Control Equipment")
        solids_layout = QFormLayout()

        self.fields = {}
        self.fields['shakers'] = FormRow.add_line_edit(
            solids_layout, "Shale Shakers:",
            "e.g., 4 x Derrick FLC-2000, API 200 mesh")
        self.fields['degasser'] = FormRow.add_line_edit(
            solids_layout, "Degasser:", "e.g., Centrifugal Degasser")
        self.fields['desander'] = FormRow.add_line_edit(
            solids_layout, "Desander:", "e.g., 12\" Desander Cones")
        self.fields['desilter'] = FormRow.add_line_edit(
            solids_layout, "Desilter:", "e.g., 4\" Desilter Cones")
        self.fields['mud_cleaner'] = FormRow.add_line_edit(
            solids_layout, "Mud Cleaner:")
        self.fields['centrifuge'] = FormRow.add_line_edit(
            solids_layout, "Centrifuge:",
            "e.g., 2 x Decanting Centrifuge 518")
        self.fields['agitators'] = FormRow.add_line_edit(
            solids_layout, "Agitators:")
        self.fields['mud_mixing'] = FormRow.add_line_edit(
            solids_layout, "Mud Mixing System:")

        grp_solids.setLayout(solids_layout)
        main_layout.addWidget(grp_solids)

        main_layout.addStretch()
        self.setWidget(container)

    def load_sample(self):
        sample = [
            ["Conductor", "36", "0", "200", "WBM - Bentonite",
             "8.8", "9.0", "45", "12", "10", "4", "8", "12",
             "8.0", "-", "9.5", "500", "10", "0.5", "-", "-",
             "500", "200", "Bentonite, CMC, Soda Ash",
             "9.0", "9.1", "Spud mud"],
            ["Surface", "26", "200", "2000",
             "WBM - KCl Polymer", "9.0", "9.5", "50", "18",
             "15", "6", "12", "18", "5.0", "12.0", "10.0",
             "2000", "15", "0.3", "-", "-", "1500", "800",
             "KCl, PHPA, Starch, PAC-R, PAC-L",
             "9.7", "9.8", ""],
            ["Intermediate", "17-1/2", "2000", "6500",
             "WBM - KCl Polymer", "9.5", "12.0", "55", "22",
             "18", "8", "14", "20", "4.0", "8.0", "10.5",
             "5000", "20", "0.2", "-", "-", "2500", "1200",
             "KCl, Polymer, Barite, LCM",
             "12.3", "12.5", "Build section"],
            ["Production", "12-1/4", "6500", "9500",
             "OBM - Mineral Oil Based", "10.5", "12.5", "55",
             "20", "12", "6", "10", "14", "-", "4.0", "-",
             "-", "-", "0.1", "80/20", "800",
             "3000", "1500",
             "Mineral Oil, CaCl2, Organophilic Clay, Barite",
             "12.8", "13.0", "Reservoir section - minimize damage"],
        ]
        self.mud_table.set_data(sample)

    def get_data(self) -> List[MudProgram]:
        muds = []
        for row in self.mud_table.get_all_data():
            if row[0]:
                mp = MudProgram()
                mp.section_name = row[0]
                try:
                    mp.hole_size = float(row[1]) if row[1] else 0
                    mp.depth_from = float(row[2]) if row[2] else 0
                    mp.depth_to = float(row[3]) if row[3] else 0
                except ValueError:
                    pass
                mp.mud_type = row[4]
                try:
                    mp.mud_weight_in = float(row[5]) if row[5] else 0
                    mp.mud_weight_out = float(row[6]) if row[6] else 0
                    mp.funnel_viscosity = float(row[7]) if row[7] else 0
                    mp.plastic_viscosity = float(row[8]) if row[8] else 0
                    mp.yield_point = float(row[9]) if row[9] else 0
                    mp.gel_strength_10s = float(row[10]) if row[10] else 0
                    mp.gel_strength_10m = float(row[11]) if row[11] else 0
                    mp.gel_strength_30m = float(row[12]) if row[12] else 0
                except ValueError:
                    pass
                try:
                    mp.fluid_loss = float(row[13]) if row[13] and row[13] != '-' else 0
                    mp.hthp_fluid_loss = float(row[14]) if row[14] and row[14] != '-' else 0
                    mp.ph = float(row[15]) if row[15] and row[15] != '-' else 0
                    mp.chlorides = float(row[16]) if row[16] and row[16] != '-' else 0
                    mp.mbt = float(row[17]) if row[17] and row[17] != '-' else 0
                    mp.sand_content = float(row[18]) if row[18] and row[18] != '-' else 0
                except ValueError:
                    pass
                mp.oil_water_ratio = row[19] if len(row) > 19 else ""
                try:
                    mp.electrical_stability = float(row[20]) if row[20] and row[20] != '-' else 0
                    mp.total_volume_required = float(row[21]) if row[21] else 0
                    mp.active_volume = float(row[22]) if row[22] else 0
                except ValueError:
                    pass
                mp.key_additives = row[23] if len(row) > 23 else ""
                try:
                    mp.ecd_at_shoe = float(row[24]) if row[24] else 0
                    mp.ecd_at_td = float(row[25]) if row[25] else 0
                except ValueError:
                    pass
                mp.remarks = row[26] if len(row) > 26 else ""
                muds.append(mp)
        return muds


# ============================================================================
# TAB: BHA & DRILLSTRING
# ============================================================================

class BHATab(QScrollArea):
    """تب طراحی BHA و رشته حفاری"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)

        # ---- BHA Summary ----
        grp_bha_summary = QGroupBox("BHA Summary - All Sections")
        bha_summary_layout = QVBoxLayout()

        self.bha_summary_table = EditableTable([
            "Section", "BHA #", "Hole Size (in)", "BHA Type",
            "Bit Type", "Bit Size (in)", "Bit Manufacturer",
            "Bit Model", "Nozzles (TFA sq.in)",
            "Motor Type", "Motor OD (in)", "Motor Bend (°)",
            "RSS Type", "MWD", "LWD Sensors",
            "Rec. WOB (klbs)", "Rec. RPM", "Rec. Flow (GPM)",
            "Max Torque (ft-lbs)", "Remarks"
        ])
        bha_summary_layout.addWidget(self.bha_summary_table)

        btn_layout = QHBoxLayout()
        btn_sample = QPushButton("📋 Load Sample BHA")
        btn_sample.clicked.connect(self.load_sample_bha)
        btn_layout.addWidget(btn_sample)
        btn_layout.addStretch()
        bha_summary_layout.addLayout(btn_layout)

        grp_bha_summary.setLayout(bha_summary_layout)
        main_layout.addWidget(grp_bha_summary)

        # ---- Drill String Details ----
        grp_ds = QGroupBox("Drill String Components Detail")
        ds_layout = QVBoxLayout()

        self.ds_table = EditableTable([
            "Section", "BHA #", "Component", "OD (in)",
            "ID (in)", "Weight (ppf)", "Length (ft)",
            "Grade", "Connection", "TJ OD (in)",
            "TJ ID (in)", "Makeup Torque (ft-lbs)",
            "Max Pull (klbs)", "Qty", "Total Length (ft)",
            "Remarks"
        ])
        ds_layout.addWidget(self.ds_table)

        grp_ds.setLayout(ds_layout)
        main_layout.addWidget(grp_ds)

        # ---- Drilling Parameters ----
        grp_params = QGroupBox("Drilling Parameters by Section")
        params_layout = QVBoxLayout()

        self.params_table = EditableTable([
            "Section", "Hole Size (in)", "Depth From (ft)",
            "Depth To (ft)", "WOB Min (klbs)", "WOB Max (klbs)",
            "RPM Min", "RPM Max", "Flow Min (GPM)",
            "Flow Max (GPM)", "Max Torque (ft-lbs)",
            "ROP Min (ft/hr)", "ROP Max (ft/hr)", "ROP Avg (ft/hr)",
            "Max SPP (psi)", "Overpull Limit (klbs)",
            "Pickup Wt (klbs)", "Slackoff Wt (klbs)",
            "Rotating Wt (klbs)", "Max ECD (ppg)",
            "Max Trip In (ft/min)", "Max Trip Out (ft/min)",
            "Remarks"
        ])
        params_layout.addWidget(self.params_table)

        grp_params.setLayout(params_layout)
        main_layout.addWidget(grp_params)

        main_layout.addStretch()
        self.setWidget(container)

    def load_sample_bha(self):
        sample = [
            ["Surface", "1", "26", "Rotary", "Tricone Insert",
             "26", "Smith Bits", "XR+", "3x22 (1.14)",
             "-", "-", "-", "-", "Gyro MWD", "-",
             "15-30", "80-120", "800-1000", "25000",
             "Hole Opening from 17-1/2\" pilot"],
            ["Intermediate", "1", "17-1/2", "Motor + MWD/LWD",
             "PDC", "17-1/2", "Baker Hughes", "Dynamus",
             "5x16, 2x14 (0.98)", "9-5/8\" Positive",
             "9-5/8", "1.5", "-", "OnTrak", "GR, RES, DEN, NEU",
             "15-35", "100-160", "700-850", "35000",
             "Build & Hold section"],
            ["Production", "1", "12-1/4", "RSS + MWD/LWD",
             "PDC", "12-1/4", "Schlumberger", "Smith SDi616",
             "4x13, 2x12 (0.68)", "-", "-", "-",
             "PowerDrive X6", "TeleScope", "GR, RES, DEN, NEU, SON",
             "10-25", "120-180", "550-700", "30000",
             "Tangent & reservoir section"],
        ]
        self.bha_summary_table.set_data(sample)

    def get_bha_data(self) -> List[BHADesign]:
        bhas = []
        for row in self.bha_summary_table.get_all_data():
            if row[0]:
                bha = BHADesign()
                bha.section_name = row[0]
                try:
                    bha.bha_number = int(row[1]) if row[1] else 1
                    bha.hole_size = float(row[2]) if row[2] else 0
                except ValueError:
                    pass
                bha.bha_type = row[3]
                bha.bit_type = row[4]
                try:
                    bha.bit_size = float(row[5]) if row[5] else 0
                except ValueError:
                    pass
                bha.bit_manufacturer = row[6]
                bha.bit_model = row[7]
                bha.bit_nozzles = row[8]
                bha.motor_type = row[9] if len(row) > 9 else ""
                try:
                    bha.motor_od = float(row[10]) if row[10] and row[10] != '-' else 0
                    bha.motor_bend = float(row[11]) if row[11] and row[11] != '-' else 0
                except ValueError:
                    pass
                bha.rss_type = row[12] if len(row) > 12 else ""
                bha.mwd_type = row[13] if len(row) > 13 else ""
                bha.lwd_sensors = row[14] if len(row) > 14 else ""
                bha.recommended_wob = row[15] if len(row) > 15 else ""
                bha.recommended_rpm = row[16] if len(row) > 16 else ""
                bha.recommended_flow_rate = row[17] if len(row) > 17 else ""
                bha.recommended_torque = row[18] if len(row) > 18 else ""
                bha.remarks = row[19] if len(row) > 19 else ""
                bhas.append(bha)
        return bhas

    def get_params_data(self) -> List[DrillingParameters]:
        params = []
        for row in self.params_table.get_all_data():
            if row[0]:
                dp = DrillingParameters()
                dp.section_name = row[0]
                try:
                    dp.hole_size = float(row[1]) if row[1] else 0
                    dp.depth_from = float(row[2]) if row[2] else 0
                    dp.depth_to = float(row[3]) if row[3] else 0
                    dp.wob_min = float(row[4]) if row[4] else 0
                    dp.wob_max = float(row[5]) if row[5] else 0
                    dp.rpm_min = float(row[6]) if row[6] else 0
                    dp.rpm_max = float(row[7]) if row[7] else 0
                    dp.flow_rate_min = float(row[8]) if row[8] else 0
                    dp.flow_rate_max = float(row[9]) if row[9] else 0
                    dp.torque_max = float(row[10]) if row[10] else 0
                    dp.rop_min = float(row[11]) if row[11] else 0
                    dp.rop_max = float(row[12]) if row[12] else 0
                    dp.rop_average = float(row[13]) if row[13] else 0
                    dp.spp_max = float(row[14]) if row[14] else 0
                    dp.overpull_limit = float(row[15]) if row[15] else 0
                    dp.pickup_weight = float(row[16]) if row[16] else 0
                    dp.slackoff_weight = float(row[17]) if row[17] else 0
                    dp.rotating_weight = float(row[18]) if row[18] else 0
                    dp.max_ecd = float(row[19]) if row[19] else 0
                    dp.max_trip_speed_in = float(row[20]) if row[20] else 0
                    dp.max_trip_speed_out = float(row[21]) if row[21] else 0
                except ValueError:
                    pass
                dp.remarks = row[22] if len(row) > 22 else ""
                params.append(dp)
        return params


# ============================================================================
# TAB: CEMENT DESIGN
# ============================================================================

class CementDesignTab(QScrollArea):
    """تب طراحی سیمانکاری"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)

        # ---- Cement Program ----
        grp_cement = QGroupBox("Cementing Program")
        cement_layout = QVBoxLayout()

        self.cement_table = EditableTable([
            "Section", "Casing OD (in)", "Hole Size (in)",
            "Shoe Depth MD (ft)", "TOC MD (ft)",
            "Lead Slurry Type", "Lead Density (ppg)",
            "Lead Yield (ft³/sk)", "Lead Volume (bbl)",
            "Lead Thickening Time (hr)",
            "Lead Comp. Strength 24hr (psi)",
            "Tail Slurry Type", "Tail Density (ppg)",
            "Tail Yield (ft³/sk)", "Tail Volume (bbl)",
            "Tail Thickening Time (hr)",
            "Tail Comp. Strength 24hr (psi)",
            "Spacer Type", "Spacer Density (ppg)",
            "Spacer Volume (bbl)",
            "Wash Type", "Wash Volume (bbl)",
            "Displacement Vol (bbl)", "Displacement Rate (bpm)",
            "Max ECD (ppg)", "Excess (%)",
            "WOC Time (hr)", "Plug Bump (psi)",
            "Stage Cementing", "CBL/CBIL Required",
            "Cement Additives", "Remarks"
        ])
        cement_layout.addWidget(self.cement_table)

        btn_layout = QHBoxLayout()
        btn_sample = QPushButton("📋 Load Sample Cement Program")
        btn_sample.clicked.connect(self.load_sample)
        btn_layout.addWidget(btn_sample)
        btn_layout.addStretch()
        cement_layout.addLayout(btn_layout)

        grp_cement.setLayout(cement_layout)
        main_layout.addWidget(grp_cement)

        main_layout.addStretch()
        self.setWidget(container)

    def load_sample(self):
        sample = [
            ["Surface", "20", "26", "2000", "0",
             "Class G", "13.0", "1.48", "250", "8",
             "500", "Class G", "15.8", "1.15", "100",
             "6", "2000", "Chemical Wash", "9.0", "30",
             "Fresh Water", "20", "350", "8", "14.5",
             "100", "12", "500", "No", "Yes",
             "Retarder, Fluid Loss Additive, Dispersant",
             "Cement to surface - verify returns"],
            ["Intermediate", "13-3/8", "17-1/2", "6500", "4000",
             "Class G + Perlite", "12.5", "1.92", "400", "10",
             "300", "Class G", "15.8", "1.15", "150",
             "8", "2500", "Spacer (Mud Push)", "10.5", "40",
             "Chemical Wash", "25", "450", "6", "16.0",
             "50", "18", "700", "No", "Yes",
             "Retarder, Fluid Loss, Anti-Gas Migration",
             ""],
            ["Production", "9-5/8", "12-1/4", "9500", "5500",
             "Class G + Microspheres", "12.0", "2.10", "350",
             "12", "250", "Class G + Silica", "16.4",
             "1.08", "120", "10", "3000",
             "Oil-Based Spacer", "11.0", "35",
             "Chemical Wash", "20", "380", "5", "17.0",
             "50", "24", "1000", "No", "Yes",
             "Retarder, FL, Gas Block, Silica Flour",
             "Critical cement job - reservoir isolation"],
        ]
        self.cement_table.set_data(sample)

    def get_data(self) -> List[CementDesign]:
        cements = []
        for row in self.cement_table.get_all_data():
            if row[0]:
                cd = CementDesign()
                cd.section_name = row[0]
                try:
                    cd.casing_od = float(row[1]) if row[1] else 0
                    cd.hole_size = float(row[2]) if row[2] else 0
                    cd.shoe_depth_md = float(row[3]) if row[3] else 0
                    cd.toc_md = float(row[4]) if row[4] else 0
                except ValueError:
                    pass
                cd.lead_slurry_type = row[5]
                try:
                    cd.lead_slurry_density = float(row[6]) if row[6] else 0
                    cd.lead_slurry_yield = float(row[7]) if row[7] else 0
                    cd.lead_slurry_volume = float(row[8]) if row[8] else 0
                    cd.lead_slurry_thickening_time = float(row[9]) if row[9] else 0
                    cd.lead_slurry_compressive_strength = float(row[10]) if row[10] else 0
                except ValueError:
                    pass
                cd.tail_slurry_type = row[11]
                try:
                    cd.tail_slurry_density = float(row[12]) if row[12] else 0
                    cd.tail_slurry_yield = float(row[13]) if row[13] else 0
                    cd.tail_slurry_volume = float(row[14]) if row[14] else 0
                    cd.tail_slurry_thickening_time = float(row[15]) if row[15] else 0
                    cd.tail_slurry_compressive_strength = float(row[16]) if row[16] else 0
                except ValueError:
                    pass
                cd.spacer_type = row[17] if len(row) > 17 else ""
                try:
                    cd.spacer_density = float(row[18]) if row[18] else 0
                    cd.spacer_volume = float(row[19]) if row[19] else 0
                except ValueError:
                    pass
                cd.wash_type = row[20] if len(row) > 20 else ""
                try:
                    cd.wash_volume = float(row[21]) if row[21] else 0
                    cd.displacement_volume = float(row[22]) if row[22] else 0
                    cd.displacement_rate = float(row[23]) if row[23] else 0
                    cd.max_ecd = float(row[24]) if row[24] else 0
                    cd.excess_percentage = float(row[25]) if row[25] else 50
                    cd.woc_time = float(row[26]) if row[26] else 0
                    cd.plug_bump_pressure = float(row[27]) if row[27] else 0
                except ValueError:
                    pass
                cd.stage_cementing = row[28].lower() == 'yes' if len(row) > 28 else False
                cd.cbl_cbil_required = row[29].lower() == 'yes' if len(row) > 29 else True
                cd.cement_additives = row[30] if len(row) > 30 else ""
                cd.remarks = row[31] if len(row) > 31 else ""
                cements.append(cd)
        return cements


# ============================================================================
# TAB: DIRECTIONAL PLAN
# ============================================================================

class DirectionalPlanTab(QScrollArea):
    """تب برنامه جهتی"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)

        # ---- Directional Parameters ----
        grp_dir = QGroupBox("Directional Drilling Parameters")
        form_dir = QFormLayout()
        form_dir.setSpacing(8)

        self.fields = {}
        self.fields['survey_tool'] = FormRow.add_combo(
            form_dir, "Survey Tool:",
            ["MWD (Magnetic)", "Gyro MWD", "Gyro While Drilling",
             "North Seeking Gyro", "Single Shot", "Multi-Shot",
             "Continuous Gyro"])
        self.fields['survey_frequency'] = FormRow.add_double_spin(
            form_dir, "Survey Interval:", 0, 500, 0, 10, "ft")
        self.fields['kop_md'] = FormRow.add_double_spin(
            form_dir, "Kickoff Point (MD):", 0, 30000, 0, 100, "ft")
        self.fields['kop_tvd'] = FormRow.add_double_spin(
            form_dir, "Kickoff Point (TVD):", 0, 30000, 0, 100, "ft")
        self.fields['build_rate'] = FormRow.add_double_spin(
            form_dir, "Build Rate:", 0, 15, 2, 0.1, "°/100ft")
        self.fields['turn_rate'] = FormRow.add_double_spin(
            form_dir, "Turn Rate:", 0, 15, 2, 0.1, "°/100ft")
        self.fields['hold_inclination'] = FormRow.add_double_spin(
            form_dir, "Hold Inclination:", 0, 90, 1, 1, "°")
        self.fields['hold_azimuth'] = FormRow.add_double_spin(
            form_dir, "Hold Azimuth:", 0, 360, 1, 1, "°")
        self.fields['target_inclination'] = FormRow.add_double_spin(
            form_dir, "Target Inclination:", 0, 90, 1, 1, "°")
        self.fields['target_azimuth'] = FormRow.add_double_spin(
            form_dir, "Target Azimuth:", 0, 360, 1, 1, "°")
        self.fields['max_dls'] = FormRow.add_double_spin(
            form_dir, "Max DLS:", 0, 20, 2, 0.1, "°/100ft")
        self.fields['horizontal_displacement'] = FormRow.add_double_spin(
            form_dir, "Horizontal Displacement:", 0, 50000, 0, 100, "ft")
        self.fields['vertical_section'] = FormRow.add_double_spin(
            form_dir, "Vertical Section:", 0, 50000, 0, 100, "ft")

        grp_dir.setLayout(form_dir)
        main_layout.addWidget(grp_dir)

        # ---- Wellpath Data ----
        grp_wp = QGroupBox("Wellpath Survey Program (Plan)")
        wp_layout = QVBoxLayout()

        self.wellpath_table = EditableTable([
            "MD (ft)", "TVD (ft)", "Inclination (°)",
            "Azimuth (°)", "DLS (°/100ft)",
            "North/South (ft)", "East/West (ft)",
            "Vertical Section (ft)", "Closure Dist (ft)",
            "Closure Dir (°)", "Build/Turn Rate",
            "Remarks"
        ])
        wp_layout.addWidget(self.wellpath_table)

        grp_wp.setLayout(wp_layout)
        main_layout.addWidget(grp_wp)

        # ---- Anti-Collision ----
        grp_ac = QGroupBox("Anti-Collision Information")
        ac_layout = QVBoxLayout()

        self.ac_table = EditableTable([
            "Reference Well", "Closest Approach MD (ft)",
            "Separation Factor", "Min Separation (ft)",
            "Action Required", "Remarks"
        ])
        ac_layout.addWidget(self.ac_table)

        grp_ac.setLayout(ac_layout)
        main_layout.addWidget(grp_ac)

        main_layout.addStretch()
        self.setWidget(container)

    def get_data(self) -> DirectionalPlan:
        dp = DirectionalPlan()
        dp.survey_tool = self.fields['survey_tool'].currentText()
        dp.survey_frequency = self.fields['survey_frequency'].value()
        dp.kickoff_point_md = self.fields['kop_md'].value()
        dp.kickoff_point_tvd = self.fields['kop_tvd'].value()
        dp.build_rate = self.fields['build_rate'].value()
        dp.turn_rate = self.fields['turn_rate'].value()
        dp.hold_inclination = self.fields['hold_inclination'].value()
        dp.hold_azimuth = self.fields['hold_azimuth'].value()
        dp.target_inclination = self.fields['target_inclination'].value()
        dp.target_azimuth = self.fields['target_azimuth'].value()
        dp.max_dls = self.fields['max_dls'].value()
        dp.horizontal_displacement = self.fields['horizontal_displacement'].value()
        dp.vertical_section = self.fields['vertical_section'].value()

        # Wellpath data
        for row in self.wellpath_table.get_all_data():
            if row[0]:
                try:
                    entry = {
                        'md': float(row[0]) if row[0] else 0,
                        'tvd': float(row[1]) if row[1] else 0,
                        'inclination': float(row[2]) if row[2] else 0,
                        'azimuth': float(row[3]) if row[3] else 0,
                        'dls': float(row[4]) if row[4] else 0,
                        'ns': row[5],
                        'ew': row[6],
                        'vs': row[7],
                        'closure_dist': row[8],
                        'closure_dir': row[9],
                        'build_turn': row[10],
                        'remarks': row[11]
                    }
                    dp.wellpath_data.append(entry)
                except (ValueError, IndexError):
                    pass
        return dp


# ============================================================================
# TAB: BOP & WELL CONTROL
# ============================================================================

class BOPWellControlTab(QScrollArea):
    """تب BOP و کنترل چاه"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)

        # ---- BOP Stack ----
        grp_bop = QGroupBox("BOP Stack Configuration")
        form_bop = QFormLayout()
        form_bop.setSpacing(8)

        self.fields = {}
        self.fields['bop_type'] = FormRow.add_combo(
            form_bop, "BOP Type:", BOPType)
        self.fields['bop_wp'] = FormRow.add_double_spin(
            form_bop, "Working Pressure:", 0, 25000, 0, 500, "psi")
        self.fields['bop_bore'] = FormRow.add_double_spin(
            form_bop, "Bore Size:", 0, 30, 3, 0.125, "in")
        self.fields['bop_manufacturer'] = FormRow.add_line_edit(
            form_bop, "Manufacturer:", "e.g., Cameron, Hydril")
        self.fields['bop_model'] = FormRow.add_line_edit(
            form_bop, "Model:")
        self.fields['annular_size'] = FormRow.add_double_spin(
            form_bop, "Annular Preventer Size:", 0, 30, 3, 0.125, "in")
        self.fields['annular_wp'] = FormRow.add_double_spin(
            form_bop, "Annular WP:", 0, 15000, 0, 500, "psi")
        self.fields['pipe_ram_size'] = FormRow.add_line_edit(
            form_bop, "Pipe Ram Size:", "e.g., 5\", 3-1/2\"")
        self.fields['blind_ram'] = FormRow.add_checkbox(
            form_bop, "Blind Rams:")
        self.fields['shear_ram'] = FormRow.add_checkbox(
            form_bop, "Shear Rams:")
        self.fields['vbr'] = FormRow.add_checkbox(
            form_bop, "Variable Bore Rams:")
        self.fields['csr'] = FormRow.add_checkbox(
            form_bop, "Casing Shear Rams:")
        self.fields['kill_line'] = FormRow.add_double_spin(
            form_bop, "Kill Line ID:", 0, 10, 3, 0.125, "in")
        self.fields['choke_line'] = FormRow.add_double_spin(
            form_bop, "Choke Line ID:", 0, 10, 3, 0.125, "in")
        self.fields['choke_manifold_wp'] = FormRow.add_double_spin(
            form_bop, "Choke Manifold WP:", 0, 25000, 0, 500, "psi")
        self.fields['accumulator_capacity'] = FormRow.add_double_spin(
            form_bop, "Accumulator Capacity:", 0, 5000, 0, 10, "gal")
        self.fields['accumulator_precharge'] = FormRow.add_double_spin(
            form_bop, "Accumulator Precharge:", 0, 5000, 0, 50, "psi")
        self.fields['diverter_size'] = FormRow.add_double_spin(
            form_bop, "Diverter Size:", 0, 50, 3, 0.125, "in")
        self.fields['diverter_line'] = FormRow.add_double_spin(
            form_bop, "Diverter Line Size:", 0, 20, 3, 0.125, "in")

        grp_bop.setLayout(form_bop)
        main_layout.addWidget(grp_bop)

        # ---- BOP Testing ----
        grp_test = QGroupBox("BOP Testing Program")
        form_test = QFormLayout()
        form_test.setSpacing(8)

        self.fields['function_test_freq'] = FormRow.add_combo(
            form_test, "Function Test Frequency:",
            ["Weekly", "Every 14 Days", "Per Regulations"])
        self.fields['pressure_test_freq'] = FormRow.add_combo(
            form_test, "Pressure Test Frequency:",
            ["Per Section", "Every 14 Days", "Per Regulations",
             "After Nipple Up", "After Repair"])
        self.fields['low_test_pressure'] = FormRow.add_double_spin(
            form_test, "Low Test Pressure:", 0, 1000, 0, 50, "psi")
        self.fields['high_test_pressure'] = FormRow.add_double_spin(
            form_test, "High Test Pressure:", 0, 25000, 0, 500, "psi")
        self.fields['test_hold_time'] = FormRow.add_double_spin(
            form_test, "Test Hold Time:", 0, 60, 0, 1, "min")

        grp_test.setLayout(form_test)
        main_layout.addWidget(grp_test)

        # ---- Well Control Data ----
        grp_wc = QGroupBox("Well Control Data")
        form_wc = QFormLayout()
        form_wc.setSpacing(8)

        self.fields['kill_method'] = FormRow.add_combo(
            form_wc, "Primary Kill Method:",
            ["Driller's Method", "Wait & Weight (Engineer's Method)",
             "Concurrent Method", "Volumetric Method",
             "Bullheading"])
        self.fields['maasp'] = FormRow.add_double_spin(
            form_wc, "MAASP at Surface:", 0, 15000, 0, 50, "psi")
        self.fields['kick_tolerance'] = FormRow.add_double_spin(
            form_wc, "Kick Tolerance:", 0, 200, 0, 5, "bbl")
        self.fields['pit_gain_alarm'] = FormRow.add_double_spin(
            form_wc, "Pit Gain Alarm Level:", 0, 50, 0, 1, "bbl")
        self.fields['slow_pump_1_spm'] = FormRow.add_double_spin(
            form_wc, "Slow Pump Rate #1:", 0, 100, 0, 5, "SPM")
        self.fields['slow_pump_1_psi'] = FormRow.add_double_spin(
            form_wc, "Slow Pump Pressure #1:", 0, 5000, 0, 50, "psi")
        self.fields['slow_pump_2_spm'] = FormRow.add_double_spin(
            form_wc, "Slow Pump Rate #2:", 0, 100, 0, 5, "SPM")
        self.fields['slow_pump_2_psi'] = FormRow.add_double_spin(
            form_wc, "Slow Pump Pressure #2:", 0, 5000, 0, 50, "psi")
        self.fields['h2s_action'] = FormRow.add_text_edit(
            form_wc, "H₂S Action Levels:", 60)
        self.fields['emergency_contacts'] = FormRow.add_text_edit(
            form_wc, "Emergency Contacts:", 80)

        grp_wc.setLayout(form_wc)
        main_layout.addWidget(grp_wc)

        main_layout.addStretch()
        self.setWidget(container)

    def get_bop_data(self) -> BOPStack:
        bs = BOPStack()
        bs.bop_type = self.fields['bop_type'].currentText()
        bs.working_pressure = self.fields['bop_wp'].value()
        bs.bore_size = self.fields['bop_bore'].value()
        bs.manufacturer = self.fields['bop_manufacturer'].text()
        bs.model = self.fields['bop_model'].text()
        bs.annular_preventer_size = self.fields['annular_size'].value()
        bs.annular_preventer_wp = self.fields['annular_wp'].value()
        bs.pipe_ram_size = self.fields['pipe_ram_size'].text()
        bs.blind_ram = self.fields['blind_ram'].isChecked()
        bs.shear_ram = self.fields['shear_ram'].isChecked()
        bs.variable_bore_ram = self.fields['vbr'].isChecked()
        bs.casing_shear_ram = self.fields['csr'].isChecked()
        bs.kill_line_size = self.fields['kill_line'].value()
        bs.choke_line_size = self.fields['choke_line'].value()
        bs.choke_manifold_wp = self.fields['choke_manifold_wp'].value()
        bs.accumulator_capacity = self.fields['accumulator_capacity'].value()
        bs.accumulator_precharge = self.fields['accumulator_precharge'].value()
        bs.diverter_size = self.fields['diverter_size'].value()
        bs.diverter_line_size = self.fields['diverter_line'].value()
        bs.function_test_frequency = self.fields['function_test_freq'].currentText()
        bs.pressure_test_frequency = self.fields['pressure_test_freq'].currentText()
        bs.bop_test_pressure_low = self.fields['low_test_pressure'].value()
        bs.bop_test_pressure_high = self.fields['high_test_pressure'].value()
        return bs

    def get_wc_data(self) -> WellControlData:
        wc = WellControlData()
        wc.kill_method = self.fields['kill_method'].currentText()
        wc.maasp_surface = self.fields['maasp'].value()
        wc.kick_tolerance = self.fields['kick_tolerance'].value()
        wc.pit_gain_action_level = self.fields['pit_gain_alarm'].value()
        wc.slow_pump_rate_1 = self.fields['slow_pump_1_spm'].value()
        wc.slow_pump_pressure_1 = self.fields['slow_pump_1_psi'].value()
        wc.slow_pump_rate_2 = self.fields['slow_pump_2_spm'].value()
        wc.slow_pump_pressure_2 = self.fields['slow_pump_2_psi'].value()
        wc.h2s_action_levels = self.fields['h2s_action'].toPlainText()
        wc.emergency_contacts = self.fields['emergency_contacts'].toPlainText()
        return wc


# ============================================================================
# TAB: RIG SPECIFICATIONS
# ============================================================================

class RigSpecTab(QScrollArea):
    """تب مشخصات دکل"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)

        self.fields = {}

        # ---- Rig General ----
        grp_general = QGroupBox("Rig General Information")
        form = QFormLayout()
        form.setSpacing(8)

        self.fields['rig_name'] = FormRow.add_line_edit(form, "Rig Name:")
        self.fields['rig_type'] = FormRow.add_combo(form, "Rig Type:", RigType)
        self.fields['rig_contractor'] = FormRow.add_line_edit(
            form, "Rig Contractor:")
        self.fields['max_hook_load'] = FormRow.add_double_spin(
            form, "Max Hook Load:", 0, 3000000, 0, 10000, "lbs")
        self.fields['drawworks_hp'] = FormRow.add_double_spin(
            form, "Drawworks Power:", 0, 5000, 0, 50, "HP")
        self.fields['top_drive'] = FormRow.add_checkbox(
            form, "Top Drive Installed:")
        self.fields['top_drive_model'] = FormRow.add_line_edit(
            form, "Top Drive Model:")
        self.fields['top_drive_torque'] = FormRow.add_double_spin(
            form, "Top Drive Max Torque:", 0, 100000, 0, 500, "ft-lbs")
        self.fields['max_rpm'] = FormRow.add_double_spin(
            form, "Max Rotary Speed:", 0, 500, 0, 10, "RPM")
        self.fields['derrick_height'] = FormRow.add_double_spin(
            form, "Derrick/Mast Height:", 0, 300, 0, 5, "ft")
        self.fields['rotary_table'] = FormRow.add_double_spin(
            form, "Rotary Table Size:", 0, 60, 2, 0.5, "in")

        grp_general.setLayout(form)
        main_layout.addWidget(grp_general)

        # ---- Mud Pumps ----
        grp_pumps = QGroupBox("Mud Pumps")
        form_pump = QFormLayout()
        form_pump.setSpacing(8)

        for i in range(1, 4):
            self.fields[f'pump{i}_type'] = FormRow.add_line_edit(
                form_pump, f"Pump #{i} Type:", "e.g., NOV 14-P-220")
            self.fields[f'pump{i}_hp'] = FormRow.add_double_spin(
                form_pump, f"Pump #{i} HP:", 0, 3000, 0, 50, "HP")
            self.fields[f'pump{i}_liner'] = FormRow.add_double_spin(
                form_pump, f"Pump #{i} Liner:", 0, 10, 3, 0.125, "in")
            self.fields[f'pump{i}_max_pressure'] = FormRow.add_double_spin(
                form_pump, f"Pump #{i} Max Pressure:", 0, 10000, 0, 100, "psi")
            self.fields[f'pump{i}_max_flow'] = FormRow.add_double_spin(
                form_pump, f"Pump #{i} Max Flow:", 0, 2000, 0, 50, "GPM")

        grp_pumps.setLayout(form_pump)
        main_layout.addWidget(grp_pumps)

        # ---- Pit System ----
        grp_pits = QGroupBox("Pit System & Solids Control")
        form_pits = QFormLayout()

        self.fields['pit_total'] = FormRow.add_double_spin(
            form_pits, "Total Pit Volume:", 0, 5000, 0, 50, "bbl")
        self.fields['pit_active'] = FormRow.add_double_spin(
            form_pits, "Active Pit Volume:", 0, 3000, 0, 50, "bbl")
        self.fields['shakers'] = FormRow.add_spin(
            form_pits, "Shale Shakers:", 0, 10)
        self.fields['degasser'] = FormRow.add_line_edit(
            form_pits, "Degasser Type:")
        self.fields['centrifuge_detail'] = FormRow.add_line_edit(
            form_pits, "Centrifuge:")
        self.fields['generators'] = FormRow.add_line_edit(
            form_pits, "Generators:", "e.g., 4 x CAT 3512, 1500kW each")
        self.fields['total_power'] = FormRow.add_double_spin(
            form_pits, "Total Power:", 0, 20000, 0, 100, "kW")
        self.fields['crane'] = FormRow.add_double_spin(
            form_pits, "Crane Capacity:", 0, 500, 0, 5, "tons")
        self.fields['accommodation'] = FormRow.add_spin(
            form_pits, "Accommodation:", 0, 300, "persons")

        grp_pits.setLayout(form_pits)
        main_layout.addWidget(grp_pits)

        main_layout.addStretch()
        self.setWidget(container)

    def get_data(self) -> RigSpecification:
        rs = RigSpecification()
        rs.rig_name = self.fields['rig_name'].text()
        rs.rig_type = self.fields['rig_type'].currentText()
        rs.rig_contractor = self.fields['rig_contractor'].text()
        rs.max_hook_load = self.fields['max_hook_load'].value()
        rs.drawworks_power = self.fields['drawworks_hp'].value()
        rs.top_drive = self.fields['top_drive'].isChecked()
        rs.top_drive_model = self.fields['top_drive_model'].text()
        rs.top_drive_torque = self.fields['top_drive_torque'].value()
        rs.max_rotary_speed = self.fields['max_rpm'].value()
        rs.derrick_height = self.fields['derrick_height'].value()
        rs.rotary_table_size = self.fields['rotary_table'].value()

        rs.mud_pump_1_type = self.fields['pump1_type'].text()
        rs.mud_pump_1_hp = self.fields['pump1_hp'].value()
        rs.mud_pump_1_liner = self.fields['pump1_liner'].value()
        rs.mud_pump_1_max_pressure = self.fields['pump1_max_pressure'].value()
        rs.mud_pump_1_max_flow = self.fields['pump1_max_flow'].value()

        rs.mud_pump_2_type = self.fields['pump2_type'].text()
        rs.mud_pump_2_hp = self.fields['pump2_hp'].value()
        rs.mud_pump_2_liner = self.fields['pump2_liner'].value()
        rs.mud_pump_2_max_pressure = self.fields['pump2_max_pressure'].value()
        rs.mud_pump_2_max_flow = self.fields['pump2_max_flow'].value()

        rs.mud_pump_3_type = self.fields['pump3_type'].text()
        rs.mud_pump_3_hp = self.fields['pump3_hp'].value()

        rs.pit_volume_total = self.fields['pit_total'].value()
        rs.pit_volume_active = self.fields['pit_active'].value()
        rs.shale_shaker_count = self.fields['shakers'].value()
        rs.degasser_type = self.fields['degasser'].text()
        rs.centrifuge = self.fields['centrifuge_detail'].text()
        rs.generators = self.fields['generators'].text()
        rs.total_power = self.fields['total_power'].value()
        rs.crane_capacity = self.fields['crane'].value()
        rs.accommodation = self.fields['accommodation'].value()

        return rs


# ============================================================================
# TAB: TIME ESTIMATE & EVALUATION
# ============================================================================

class TimeEstimateTab(QScrollArea):
    """تب تخمین زمان و ارزیابی"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)

        # ---- Time Estimate ----
        grp_time = QGroupBox("Time vs Depth Estimate (AFE)")
        time_layout = QVBoxLayout()

        self.time_table = EditableTable([
            "Section", "Operation", "Depth From (ft)",
            "Depth To (ft)", "ROP Avg (ft/hr)",
            "Drilling Time (hr)", "Trip Time (hr)",
            "Circulating Time (hr)", "Connection Time (hr)",
            "Logging Time (hr)", "Casing Run Time (hr)",
            "Cementing Time (hr)", "WOC Time (hr)",
            "BOP/Nipple Time (hr)", "Flat Time (hr)",
            "NPT Contingency (%)", "Section Days",
            "Cumulative Days", "Remarks"
        ])
        time_layout.addWidget(self.time_table)

        btn_layout = QHBoxLayout()
        btn_sample = QPushButton("📋 Load Sample Time Estimate")
        btn_sample.clicked.connect(self.load_sample)
        btn_layout.addWidget(btn_sample)
        btn_auto = QPushButton("🔄 Auto-Calculate")
        btn_auto.clicked.connect(self.auto_calculate)
        btn_layout.addWidget(btn_auto)
        btn_layout.addStretch()
        time_layout.addLayout(btn_layout)

        grp_time.setLayout(time_layout)
        main_layout.addWidget(grp_time)

        # ---- Evaluation Program ----
        grp_eval = QGroupBox("Evaluation Program (Logging & Coring)")
        eval_layout = QVBoxLayout()

        self.eval_table = EditableTable([
            "Section", "Evaluation Type", "Tool/Service",
            "Interval From (ft)", "Interval To (ft)",
            "Service Provider", "Duration (hr)",
            "Purpose", "Remarks"
        ])
        eval_layout.addWidget(self.eval_table)

        btn_eval = QPushButton("📋 Load Sample Evaluation Program")
        btn_eval.clicked.connect(self.load_sample_eval)
        eval_btn_layout = QHBoxLayout()
        eval_btn_layout.addWidget(btn_eval)
        eval_btn_layout.addStretch()
        eval_layout.addLayout(eval_btn_layout)

        grp_eval.setLayout(eval_layout)
        main_layout.addWidget(grp_eval)

        main_layout.addStretch()
        self.setWidget(container)

    def load_sample(self):
        sample = [
            ["Pre-Spud", "Rig Move & Setup", "0", "0", "-",
             "0", "0", "0", "0", "0", "0", "0", "0", "48",
             "24", "10", "3.0", "3.0", "Mobilization"],
            ["Conductor", "Drill & Set 30\" Conductor", "0",
             "200", "30", "7", "0", "2", "1", "0", "6",
             "4", "12", "4", "2", "10", "1.5", "4.5",
             "Including diverter installation"],
            ["Surface", "Drill 26\" & Set 20\" Casing", "200",
             "2000", "40", "45", "8", "4", "4", "0", "18",
             "8", "12", "8", "4", "10", "5.0", "9.5", ""],
            ["Intermediate", "Drill 17-1/2\" & Set 13-3/8\"",
             "2000", "6500", "25", "180", "16", "8", "12",
             "24", "24", "12", "18", "8", "6", "10",
             "13.0", "22.5", "Including LOT"],
            ["Production", "Drill 12-1/4\" & Set 9-5/8\"",
             "6500", "9500", "15", "200", "20", "10", "16",
             "36", "30", "14", "24", "8", "8", "10",
             "16.0", "38.5", "Including evaluation"],
            ["Completion", "Completion Operations", "9500",
             "9500", "-", "0", "0", "0", "0", "0", "0",
             "0", "0", "0", "96", "10", "4.5", "43.0",
             "Completion & testing"],
        ]
        self.time_table.set_data(sample)

    def load_sample_eval(self):
        sample = [
            ["Surface", "Wireline Logging", "GR-CCL",
             "200", "2000", "Schlumberger", "8",
             "Correlation & cement evaluation", ""],
            ["Intermediate", "Wireline Logging",
             "GR-RES-DEN-NEU-SON", "2000", "6500",
             "Schlumberger", "24",
             "Formation evaluation", ""],
            ["Intermediate", "CBL/VDL", "CBL-VDL",
             "2000", "6500", "Schlumberger", "12",
             "Cement evaluation", "After WOC"],
            ["Production", "Wireline Logging",
             "GR-RES-DEN-NEU-SON-FMI-MDT", "6500",
             "9500", "Schlumberger", "36",
             "Full reservoir evaluation", ""],
            ["Production", "Coring", "Conventional Core",
             "8500", "8600", "CoreLab", "24",
             "Reservoir rock properties", "100 ft core"],
            ["Production", "CBL/CBIL", "CBL-CBIL",
             "5500", "9500", "Schlumberger", "12",
             "Cement integrity evaluation", "After WOC"],
            ["Production", "DST", "DST String",
             "8500", "9000", "Halliburton", "48",
             "Deliverability test", ""],
        ]
        self.eval_table.set_data(sample)

    def auto_calculate(self):
        """محاسبه خودکار"""
        QMessageBox.information(
            self, "Info",
            "Auto-calculation based on section depths and average ROPs.\n"
            "Please ensure formation and casing data tabs are filled first."
        )

    def get_time_data(self) -> List[TimeEstimate]:
        estimates = []
        for row in self.time_table.get_all_data():
            if row[0]:
                te = TimeEstimate()
                te.section_name = row[0]
                te.operation = row[1]
                try:
                    te.depth_from = float(row[2]) if row[2] and row[2] != '-' else 0
                    te.depth_to = float(row[3]) if row[3] and row[3] != '-' else 0
                    te.rop_average = float(row[4]) if row[4] and row[4] != '-' else 0
                    te.total_section_days = float(row[16]) if row[16] else 0
                    te.cumulative_days = float(row[17]) if row[17] else 0
                except (ValueError, IndexError):
                    pass
                te.remarks = row[18] if len(row) > 18 else ""
                estimates.append(te)
        return estimates


# ============================================================================
# MAIN WINDOW
# ============================================================================

class DrillingProgramMainWindow(QMainWindow):
    """پنجره اصلی نرم‌افزار"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Drilling Program Generator Pro v3.1 | "
            "Professional Drilling Program & Procedure Generator"
        )
        self.setMinimumSize(1400, 900)
        self.project = WellProject()

        self.setup_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_statusbar()
    
        self.showMaximized()
        logger.info("Application started successfully")

    def setup_ui(self):
        """ساخت رابط کاربری"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header = QLabel(
            "🛢️ DRILLING PROGRAM & PROCEDURE GENERATOR | PROFESSIONAL EDITION"
        )
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #e94560;
            padding: 15px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0f3460, stop:0.5 #16213e, stop:1 #0f3460);
            border-radius: 8px;
            border: 2px solid #e94560;
        """)
        main_layout.addWidget(header)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.setDocumentMode(True)

        # Create all tabs
        self.tab_dashboard = DashboardTab(self)
        self.tab_company = CompanyWellTab()
        self.tab_formation = FormationHazardTab()
        self.tab_casing = CasingDesignTab()
        self.tab_mud = MudProgramTab()
        self.tab_bha = BHATab()
        self.tab_cement = CementDesignTab()
        self.tab_directional = DirectionalPlanTab()
        self.tab_bop = BOPWellControlTab()
        self.tab_rig = RigSpecTab()
        self.tab_time = TimeEstimateTab()
        self.tab_engineering = EngineeringToolsTab()
        self.tab_risk = RiskAnalyzerTab()
        self.tab_cost = CostPricingTab()

        # Add tabs
        self.tabs.addTab(self.tab_dashboard, "🏠 Home")
        self.tabs.addTab(self.tab_company, "🏢 Company & Well")
        self.tabs.addTab(self.tab_formation, "🪨 Formations & Hazards")
        self.tabs.addTab(self.tab_casing, "🔧 Casing Design")
        self.tabs.addTab(self.tab_mud, "🧪 Mud Program")
        self.tabs.addTab(self.tab_bha, "⚙️ BHA & Drill String")
        self.tabs.addTab(self.tab_cement, "🏗️ Cement Design")
        self.tabs.addTab(self.tab_directional, "🧭 Directional Plan")
        self.tabs.addTab(self.tab_bop, "🔴 BOP & Well Control")
        self.tabs.addTab(self.tab_rig, "🏗️ Rig Specifications")
        self.tabs.addTab(self.tab_time, "⏱️ Time & Evaluation")
        self.tabs.addTab(self.tab_engineering, "🧮 Engineering Tools")
        self.tabs.addTab(self.tab_risk, "⛽ Risk Analyzer")
        self.tabs.addTab(self.tab_cost, "💰 Cost & Pricing")

        main_layout.addWidget(self.tabs, 1)

        # Bottom - Generate Button
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.progress = QProgressBar()
        self.progress.setMinimumWidth(300)
        self.progress.setVisible(False)
        bottom_layout.addWidget(self.progress)

        self.btn_generate = QPushButton(
            "📄 GENERATE DRILLING PROGRAM DOCUMENT"
        )
        self.btn_generate.setObjectName("generateBtn")
        self.btn_generate.clicked.connect(self.generate_document)
        bottom_layout.addWidget(self.btn_generate)

        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)

    def open_tab(self, tab_key: str):
        """Switch to one of the main tabs by key."""
        keys = {
            "home": 0, "company": 1, "formation": 2, "casing": 3,
            "mud": 4, "bha": 5, "cement": 6, "directional": 7,
            "bop": 8, "rig": 9, "time": 10, "engineering": 11,
            "risk": 12,
        }
        idx = keys.get(tab_key)
        if idx is not None and 0 <= idx < self.tabs.count():
            self.tabs.setCurrentIndex(idx)
        return idx is not None

    def setup_menus(self):
        """ساخت منوها"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("🆕 New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        open_action = QAction("📂 Open Project", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

        save_action = QAction("💾 Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        rev_action = QAction("🕘 Project Revisions (Restore)...", self)
        rev_action.triggered.connect(self._show_project_revisions)
        file_menu.addAction(rev_action)

        witsml_action = QAction("📡 Export WITSML / JSON (Telemetry)...", self)
        witsml_action.triggered.connect(self._export_witsml)
        file_menu.addAction(witsml_action)

        file_menu.addSeparator()

        export_action = QAction("📤 Export to Word", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.generate_document)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("🚪 Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools Menu (integrated modules)
        tools_menu = menubar.addMenu("&Tools")

        wizard_action = QAction("🧙 Program / Procedure Wizard...", self)
        wizard_action.setShortcut("Ctrl+W")
        wizard_action.triggered.connect(self._show_wizard)
        tools_menu.addAction(wizard_action)

        tools_menu.addSeparator()

        risk_action = QAction("⛽ Risk Analyzer", self)
        risk_action.setShortcut("F6")
        risk_action.triggered.connect(lambda: self.open_tab("risk"))
        tools_menu.addAction(risk_action)

        eng_action = QAction("🧮 Engineering Tools", self)
        eng_action.setShortcut("F7")
        eng_action.triggered.connect(lambda: self.open_tab("engineering"))
        tools_menu.addAction(eng_action)

        tools_menu.addSeparator()

        proc_mgr = QAction("📋 Procedure Manager...", self)
        proc_mgr.setShortcut("Ctrl+P")
        proc_mgr.triggered.connect(self._show_procedure_manager)
        tools_menu.addAction(proc_mgr)

        tb_action = QAction("⏱️ Time Breakdown Editor...", self)
        tb_action.setShortcut("Ctrl+B")
        tb_action.triggered.connect(self._show_time_breakdown)
        ops_action = QAction("📊 Operations (Readiness/NPT/Lessons)", self)
        ops_action.triggered.connect(self._show_operations)
        tools_menu.addAction(ops_action)
        wr_action = QAction("📘 Well Engineering Report (full)", self)
        wr_action.triggered.connect(self._show_well_report)
        tools_menu.addAction(wr_action)
        bk_action = QAction("💾 Backup / Restore", self)
        bk_action.triggered.connect(self._show_backup)
        tools_menu.addAction(bk_action)
        rep_action = QAction("📊 Statistical Reports & Excel Export", self)
        rep_action.triggered.connect(self._show_reports)
        tools_menu.addAction(rep_action)
        tools_menu.addAction(tb_action)

        # Templates Menu
        template_menu = menubar.addMenu("&Templates")

        pa = QAction("🛢️ Professional Well Templates...", self)
        pa.setShortcut("Ctrl+T")
        pa.triggered.connect(self._show_preset_dialog)
        template_menu.addAction(pa)

        op_action = QAction("⚙️ Operational Template Library...", self)
        op_action.setShortcut("Ctrl+Shift+T")
        op_action.triggered.connect(self._show_operational_templates)
        template_menu.addAction(op_action)

        template_menu.addSeparator()

        # Quick load shortcuts
        quick_presets = [
            ("🏜️ Middle East H₂S Well (Quick)", 'me_dev_h2s'),
            ("🛢️ Middle East Sweet Well (Quick)", 'me_dev_sweet'),
            ("🌊 Offshore Jack-Up Well (Quick)", 'offshore_jackup'),
            ("🏔️ North Sea HPHT Well (Quick)", 'north_sea_hpht'),
            ("🚢 GOM Deepwater Well (Quick)", 'gom_deepwater'),
            ("↔️ Horizontal Shale Well (Quick)", 'horizontal_shale'),
        ]
        for label, key in quick_presets:
            act = QAction(label, self)
            act.triggered.connect(
                lambda checked=False, k=key: self._quick_load_preset(k))
            template_menu.addAction(act)

        template_menu.addSeparator()

        t2 = QAction("🌊 Offshore - Exploration Well", self)
        t2.triggered.connect(lambda: self.load_template("offshore_exp"))
        template_menu.addAction(t2)

        t3 = QAction("🏔️ HPHT Well Template", self)
        t3.triggered.connect(lambda: self.load_template("hpht"))
        template_menu.addAction(t3)

        t4 = QAction("↔️ Horizontal / ERD Well", self)
        t4.triggered.connect(lambda: self.load_template("horizontal"))
        template_menu.addAction(t4)

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        standards_action = QAction("📚 Standards Reference", self)
        standards_action.triggered.connect(self.show_standards)
        help_menu.addAction(standards_action)

    def _show_wizard(self):
        """راه‌اندازی ویزارد تولید برنامه/پروسیجر"""
        try:
            path = run_wizard(self)
            if path:
                self.statusBar().showMessage(
                    f"✅ Generated: {path}")
        except Exception as e:
            import traceback
            QMessageBox.critical(
                self, "Wizard Error",
                f"{str(e)}\n\n{traceback.format_exc()[-500:]}")

    def _show_operational_templates(self):
        """Operational Templates"""
        try:
            from operational_templates import OperationalTemplateDialog
            dialog = OperationalTemplateDialog(self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(
                self, "Module Not Found",
                f"template_ui.py not found.\n{e}")
        except Exception as e:
            import traceback
            QMessageBox.critical(
                self, "Error",
                f"{str(e)}\n\n"
                f"{traceback.format_exc()[-500:]}")
                
    def _show_time_breakdown(self):
        """نمایش ادیتور Time Breakdown"""
        try:
            from time_breakdown import TimeBreakdownDialog
            dialog = TimeBreakdownDialog(self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Module Not Found",
                f"time_breakdown.py not found.\n{e}")
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error",
                f"{str(e)}\n\n{traceback.format_exc()[-500:]}")
                
    def _show_operations(self):
        """نمایش دیالوگ عملیات (Readiness / Lessons / NPT / Plan vs Actual)"""
        try:
            from operations_ui import OperationsDialog
            well_data = {}
            # pull current inputs from the company/well tab when available
            try:
                tw = self.tab_company
                for attr in ("well_name_edit", "well_name", "txt_well_name"):
                    w = getattr(tw, attr, None)
                    if w is not None and hasattr(w, "text"):
                        well_data["well_name"] = w.text()
                        break
                for attr in ("field_name_edit", "field_name", "txt_field"):
                    w = getattr(tw, attr, None)
                    if w is not None and hasattr(w, "text"):
                        well_data["field_name"] = w.text()
                        break
            except Exception:
                pass
            dlg = OperationsDialog(self, well_data=well_data)
            dlg.exec()
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Operations", f"{e}\n\n"
                                 f"{traceback.format_exc()[-300:]}")

    def _show_well_report(self):
        """تولید گزارش جامع مهندسی چاه (Word)"""
        try:
            from well_report import generate_well_report_docx, _demo_values
            from PySide6.QtWidgets import QFileDialog
            default = str(Path.home() / "Well_Engineering_Report.docx")
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Well Engineering Report", default,
                "Word Document (*.docx)")
            if not path:
                return
            # collect current values from the company tab when available
            values = _demo_values()
            try:
                tw = self.tab_company
                for attr in ("well_name_edit", "well_name", "txt_well_name"):
                    w = getattr(tw, attr, None)
                    if w is not None and hasattr(w, "text") and w.text():
                        values["well_name"] = w.text()
                        break
                for attr in ("field_name_edit", "field_name", "txt_field"):
                    w = getattr(tw, attr, None)
                    if w is not None and hasattr(w, "text") and w.text():
                        values["field_name"] = w.text()
                        break
            except Exception:
                pass
            ok = generate_well_report_docx(values, path)
            QMessageBox.information(
                self, "Report",
                f"Well Engineering Report generated:\n{path}"
                if ok else "Generation failed.")
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Well Report", f"{e}\n\n"
                                 f"{traceback.format_exc()[-300:]}")

    def _show_backup(self):
        """پشتیبانگیری / بازیابی دیتابیسها (با پشتیبانی رمزنگاری)"""
        try:
            from backup_restore import (create_backup, list_backups,
                                        restore_backup)
            backups = list_backups()
            if not backups:
                create_backup()
                backups = list_backups()
            names = [b["name"] for b in backups]
            from PySide6.QtWidgets import QInputDialog
            choice, ok = QInputDialog.getItem(
                self, "Backup / Restore",
                "Select a backup to restore (or Cancel to create a new one):\n\n"
                "🔒 = password-protected (encrypted at rest)",
                names, 0, False)
            if ok and choice:
                password = None
                if choice.endswith(".enc"):
                    password, pok = QInputDialog.getText(
                        self, "Encrypted Backup",
                        "Enter the backup password:", QLineEdit.Password)
                    if not pok:
                        return
                res = restore_backup(choice, password=password)
                if res.get("error"):
                    QMessageBox.critical(self, "Restore",
                                         f"Failed: {res['error']}")
                    return
                n_ok = sum(1 for v in res.values() if v)
                QMessageBox.information(
                    self, "Restore",
                    f"Restored {n_ok}/{len(res)} files from {choice}")
            else:
                enc, eok = QMessageBox.question(
                    self, "Backup",
                    "Create a password-protected (encrypted) backup?\n\n"
                    "Yes = encrypted .enc archive   |   No = plain folder",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if enc == QMessageBox.Cancel:
                    return
                password = None
                if enc == QMessageBox.Yes:
                    p1, ok1 = QInputDialog.getText(
                        self, "Encrypted Backup",
                        "Set a password for the backup:",
                        QLineEdit.Password)
                    if not ok1 or not p1:
                        return
                    p2, ok2 = QInputDialog.getText(
                        self, "Confirm Password",
                        "Repeat the password:", QLineEdit.Password)
                    if not ok2 or p1 != p2:
                        QMessageBox.warning(self, "Backup",
                                            "Passwords do not match.")
                        return
                    password = p1
                b = create_backup(password=password)
                QMessageBox.information(
                    self, "Backup",
                    f"Backup created: {b.name if b else 'failed'}"
                    + (" (encrypted 🔒)" if password else ""))
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Backup", f"{e}\n\n"
                                 f"{traceback.format_exc()[-300:]}")

    def _export_witsml(self):
        """Export the current project as WITSML XML + JSON handoff."""
        try:
            from witsml_export import export_witsml, export_json
            project = self.collect_all_data()
            ci = project.company_info
            values = {
                "well_name": ci.well_name, "field_name": ci.field_name,
                "operator": ci.operator_name,
                "well_type": project.well_info.well_type,
                "rig_name": project.rig_spec.rig_type,
            }
            # merge tab data that maps to basis keys
            for tab_key, tab in (("mud_weight", self.tab_mud),
                                 ("hole_size", self.tab_casing)):
                pass
            folder = QFileDialog.getExistingDirectory(
                self, "Select Export Folder",
                str(Path.cwd() / "projects" / "exports"))
            if not folder:
                return
            base = (ci.well_name or "well").replace(" ", "_")
            p1 = export_witsml(values, str(Path(folder) / f"{base}.xml"))
            p2 = export_json(values, str(Path(folder) / f"{base}.json"))
            QMessageBox.information(
                self, "WITSML Exported",
                f"Exported:\n{p1}\n{p2}\n\n"
                "(wellbore trajectory stations are included when the "
                "trajectory table is filled in the wizard)")
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "WITSML Export", f"{e}\n\n"
                                 f"{traceback.format_exc()[-300:]}")

    def _show_reports(self):
        """Statistical reports preview + Excel export dialog."""
        try:
            import reporting
            dlg = QDialog(self)
            dlg.setWindowTitle("📊 Statistical Reports")
            dlg.setMinimumSize(860, 640)
            lay = QVBoxLayout(dlg)
            tabs = QTabWidget()
            preview = QTextEdit()
            preview.setReadOnly(True)
            md = reporting.report_markdown("all")
            preview.setPlainText(md)
            tabs.addTab(preview, "📄 Report (Markdown)")
            btns = QHBoxLayout()
            btn_xls = QPushButton("📗 Export Excel Report…")
            def _export():
                path, _ = QFileDialog.getSaveFileName(
                    dlg, "Save Excel Report",
                    f"Drilling_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "Excel Files (*.xlsx)")
                if path:
                    n = reporting.export_report_excel(path, "all")
                    QMessageBox.information(
                        dlg, "Exported",
                        f"Excel report saved with {n} sheets:\n{path}")
            btn_xls.clicked.connect(_export)
            btns.addStretch()
            btn_xls.setMinimumWidth(220)
            btns.addWidget(btn_xls)
            lay.addWidget(tabs)
            lay.addLayout(btns)
            dlg.exec()
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Reports", f"{e}\n\n"
                                 f"{traceback.format_exc()[-300:]}")

    def _show_procedure_manager(self):
        """نمایش مدیریت پروسیجرها با دیتابیس"""
        try:
            from procedures_db import ProcedureManagerDialog
            dialog = ProcedureManagerDialog(self)
            dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Module Not Found",
                f"procedures_db.py not found.\n{e}")
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error",
                f"{str(e)}\n\n{traceback.format_exc()[-500:]}")
                
    def _show_preset_dialog(self):
        try:
            import importlib
            pm = importlib.import_module('presets_module')
            d = pm.PresetSelectorDialog(self)
            d.presetSelected.connect(lambda p: pm.load_project_into_gui(self, p))
            d.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
    def setup_toolbar(self):
        """ساخت نوار ابزار"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)

        btn_new = QPushButton("🆕 New")
        btn_new.clicked.connect(self.new_project)
        toolbar.addWidget(btn_new)

        btn_open = QPushButton("📂 Open")
        btn_open.clicked.connect(self.open_project)
        toolbar.addWidget(btn_open)

        btn_save = QPushButton("💾 Save")
        btn_save.clicked.connect(self.save_project)
        toolbar.addWidget(btn_save)

        toolbar.addSeparator()

        btn_validate = QPushButton("✅ Validate Data")
        btn_validate.clicked.connect(self.validate_data)
        toolbar.addWidget(btn_validate)

        btn_preview = QPushButton("👁️ Preview")
        btn_preview.clicked.connect(self.preview_document)
        toolbar.addWidget(btn_preview)

        toolbar.addSeparator()

        btn_wizard = QPushButton("🧙 Wizard")
        btn_wizard.clicked.connect(self._show_wizard)
        toolbar.addWidget(btn_wizard)

        btn_risk = QPushButton("⛽ Risk Analyzer")
        btn_risk.clicked.connect(lambda: self.open_tab("risk"))
        toolbar.addWidget(btn_risk)

        btn_eng = QPushButton("🧮 Engineering")
        btn_eng.clicked.connect(lambda: self.open_tab("engineering"))
        toolbar.addWidget(btn_eng)

        toolbar.addSeparator()

        btn_gen = QPushButton("📄 Generate Word Document")
        btn_gen.clicked.connect(self.generate_document)
        toolbar.addWidget(btn_gen)

    def setup_statusbar(self):
        """ساخت نوار وضعیت"""
        self.statusBar().showMessage(
            "Ready | Fill in all tabs and click Generate to create "
            "the Drilling Program Document"
        )

    def collect_all_data(self) -> WellProject:
        """جمع‌آوری تمام داده‌ها از تب‌ها"""
        project = WellProject()

        # Tab 1: Company & Well
        project.company_info, project.well_info = self.tab_company.get_data()

        # Tab 2: Formations & Hazards
        project.formation_tops = self.tab_formation.get_formation_data()
        project.hazards = self.tab_formation.get_hazard_data()

        # Tab 3: Casing
        project.casing_design = self.tab_casing.get_data()

        # Tab 4: Mud
        project.mud_programs = self.tab_mud.get_data()

        # Tab 5: BHA
        project.bha_designs = self.tab_bha.get_bha_data()
        project.drilling_parameters = self.tab_bha.get_params_data()

        # Tab 6: Cement
        project.cement_design = self.tab_cement.get_data()

        # Tab 7: Directional
        project.directional_plan = self.tab_directional.get_data()

        # Tab 8: BOP & Well Control
        project.bop_stack = self.tab_bop.get_bop_data()
        project.well_control = self.tab_bop.get_wc_data()

        # Tab 9: Rig
        project.rig_spec = self.tab_rig.get_data()

        # Tab 10: Time & Evaluation
        project.time_estimates = self.tab_time.get_time_data()

        return project



    def generate_document(self):

        try:
            project = self.collect_all_data()

            try:
                from docx import Document
            except ImportError:
                QMessageBox.warning(
                    self, "Missing Dependency",
                    "python-docx is required.\n"
                    "Run: pip install python-docx")
                return


            try:
                from word_generator_enhanced import (
                    FormatSelectorDialog,
                    MultiFormatDrillingDocument,
                    ReportFormat
                )
                fmt_dialog = FormatSelectorDialog(self)
                if fmt_dialog.exec() != QDialog.Accepted:
                    return
                selected_fmt = fmt_dialog.get_selected_format()
            except ImportError:
                # Enhanced format selector not installed - use word_generator
                from word_generator import ReportFormat
                selected_fmt = ReportFormat.STANDARD


            fmt_suffix = {
                ReportFormat.STANDARD: "",
                ReportFormat.COMPACT: "_Compact",
                ReportFormat.EXECUTIVE: "_Executive",
                ReportFormat.LANDSCAPE: "_Landscape",
                ReportFormat.FIELD: "_Field",
                ReportFormat.PRESENTATION: "_Presentation",
            }.get(selected_fmt, "")

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Drilling Program",
                f"Drilling_Program_"
                f"{project.company_info.well_name or 'Well'}"
                f"{fmt_suffix}_"
                f"Rev{project.company_info.revision}.docx",
                "Word Documents (*.docx)")

            if not file_path:
                return

            self.progress.setVisible(True)
            self.progress.setValue(0)
            self.statusBar().showMessage(
                f"Generating {selected_fmt} document...")
            QApplication.processEvents()


            try:
                from word_generator_enhanced import (
                    MultiFormatDrillingDocument)
                generator = MultiFormatDrillingDocument(
                    project)
                success = generator.generate(
                    file_path, selected_fmt, self.progress)
            except ImportError:
                from word_generator import (
                    DrillingProgramWordGenerator)
                gen = DrillingProgramWordGenerator(project)
                gen.generate(file_path, self.progress)
                success = True

            self.progress.setValue(100)
            if success:
                self.statusBar().showMessage(
                    f"? Document generated: {file_path}")
                QMessageBox.information(
                    self, "? Success",
                    f"Document generated!\n\n"
                    f"Format: "
                    f"{ReportFormat.DESCRIPTIONS.get(selected_fmt, selected_fmt)}\n"
                    f"File: {file_path}")

                if os.name == 'nt':
                    os.startfile(file_path)

        except Exception as e:
            import logging, traceback
            logging.getLogger('DrillingProgram').error(
                f"Error: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Error",
                f"Error generating document:\n{str(e)}")
        finally:
            self.progress.setVisible(False)
            
    def new_project(self):
        reply = QMessageBox.question(
            self, "New Project",
            "Create a new project? All unsaved data will be lost.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.project = WellProject()
            self.reset_all_tabs()
            self.statusBar().showMessage("✅ New project created")
            self.open_tab("company")

    def reset_all_tabs(self):
        """Reset every data-entry tab to its initial empty state."""
        from PySide6.QtWidgets import (QLineEdit, QComboBox, QDoubleSpinBox,
                                       QSpinBox, QTextEdit, QDateEdit)

        for tab in (self.tab_company, self.tab_casing, self.tab_mud,
                    self.tab_bha, self.tab_cement, self.tab_directional,
                    self.tab_bop, self.tab_rig, self.tab_time,
                    self.tab_formation):
            # Reset form fields
            fields = getattr(tab, 'fields', None)
            if isinstance(fields, dict):
                for widget in fields.values():
                    try:
                        if isinstance(widget, (QLineEdit,)):
                            widget.clear()
                        elif isinstance(widget, QTextEdit):
                            widget.clear()
                        elif isinstance(widget, QComboBox):
                            widget.setCurrentIndex(0)
                        elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                            widget.setValue(widget.minimum())
                        elif isinstance(widget, QDateEdit):
                            widget.setDate(QDate.currentDate())
                        elif hasattr(widget, 'setChecked'):
                            widget.setChecked(False)
                    except Exception:
                        pass
            # Reset editable tables
            for attr, widget in vars(tab).items():
                if attr.startswith('_'):
                    continue
                try:
                    if hasattr(widget, 'clear_all'):
                        # EditableTable - clear without confirmation dialog
                        widget.table.setRowCount(0)
                except Exception:
                    pass

    def save_project(self):
        """ذخیره پروژه در دیتابیس"""
        project = self.collect_all_data()

        if not project.company_info.well_name:
            QMessageBox.warning(self, "Warning",
                "Please enter a Well Name before saving.")
            return

        try:
            from drilling_database import DrillingProjectDatabase
            db = DrillingProjectDatabase()

            name, ok = QInputDialog.getText(
                self, "Save Project",
                "Project Name:",
                text=project.company_info.well_name)

            if ok and name:
                proj_id = db.save_project(project, name)
                db.close()
                self.statusBar().showMessage(
                    f"✅ Project saved: {name} (ID: {proj_id})")
                self.tab_dashboard.refresh_stats()
                QMessageBox.information(
                    self, "Saved",
                    f"Project '{name}' saved to database!")
            else:
                db.close()

        except ImportError:
            # Fallback to JSON
            self._save_project_json()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def open_project(self):
        """باز کردن پروژه از دیتابیس"""
        try:
            from drilling_database import DrillingProjectDatabase
            db = DrillingProjectDatabase()
            projects = db.get_all_projects()

            if not projects:
                QMessageBox.information(
                    self, "No Projects",
                    "No saved projects found.\n"
                    "Use File → Open to load a JSON file.")
                db.close()
                return

            # Show project list
            items = []
            for p in projects:
                items.append(
                    f"{p['name']} | {p['well_name']} | "
                    f"{p['operator']} | {p['modified']}")

            item, ok = QInputDialog.getItem(
                self, "Open Project",
                "Select a project:", items, 0, False)

            if ok and item:
                idx = items.index(item)
                proj_data = db.load_project(projects[idx]['id'])
                db.close()

                if proj_data and proj_data.get('data'):
                    self._load_project_from_dict(proj_data['data'])
                    self.statusBar().showMessage(
                        f"✅ Loaded: {projects[idx]['name']}")
                    self.tab_dashboard.refresh_stats()
            else:
                db.close()

        except ImportError:
            self._open_project_json()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _open_project_by_id(self, project_id):
        """باز کردن پروژه از دیتابیس با شناسه (استفاده در داشبورد)"""
        try:
            from drilling_database import DrillingProjectDatabase
            db = DrillingProjectDatabase()
            proj_data = db.load_project(project_id)
            db.close()
            if proj_data and proj_data.get('data'):
                self._load_project_from_dict(proj_data['data'])
                self.statusBar().showMessage(
                    f"✅ Loaded: {proj_data.get('name', project_id)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _show_project_revisions(self):
        """List a project's revision snapshots and restore one (buyer Q4)."""
        try:
            from drilling_database import DrillingProjectDatabase
            db = DrillingProjectDatabase()
            projects = db.get_all_projects()
            if not projects:
                QMessageBox.information(
                    self, "No Projects",
                    "No saved projects found. Save a project first, then "
                    "every save creates a restorable revision snapshot.")
                db.close()
                return
            items = [f"{p['name']} | {p['well_name']} | {p['modified']}"
                     for p in projects]
            item, ok = QInputDialog.getItem(self, "Select Project",
                                            "Project:", items, 0, False)
            if not ok:
                db.close()
                return
            idx = items.index(item)
            pid = projects[idx]['id']
            revs = db.list_revisions(pid)
            if not revs:
                QMessageBox.information(
                    self, "No Revisions",
                    "This project has no revision snapshots yet.")
                db.close()
                return
            rev_items = [f"Rev {r['revision']} | {r['created_date']} | "
                         f"{r['note']}" for r in revs]
            rev_item, ok2 = QInputDialog.getItem(
                self, "Restore Revision",
                "Restoring replaces the current project data with the "
                "selected version (current data is kept as a new "
                "snapshot):\n\nSelect a revision:", rev_items, 0, False)
            if ok2 and rev_item:
                r = revs[rev_items.index(rev_item)]
                ret = QMessageBox.question(
                    self, "Confirm Restore",
                    f"Restore revision {r['revision']} "
                    f"({r['created_date']})?\n\n"
                    "The current project state will be snapshotted first.",
                    QMessageBox.Yes | QMessageBox.No)
                if ret == QMessageBox.Yes:
                    cur = db.load_project(pid)
                    if cur and cur.get('data'):
                        db._snapshot(pid, json.dumps(
                            cur['data'], ensure_ascii=False), "Pre-restore")
                    if db.restore_revision(pid, r['revision']):
                        self._open_project_by_id(pid)
                        self.statusBar().showMessage(
                            f"✅ Restored revision {r['revision']}")
                        QMessageBox.information(
                            self, "Restored",
                            f"Project restored to revision "
                            f"{r['revision']} ({r['created_date']}).")
                    else:
                        QMessageBox.critical(self, "Restore Failed",
                                             "Revision not found.")
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _save_project_json(self):
        """Fallback: ذخیره JSON"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project",
            "drilling_project.json", "JSON Files (*.json)")
        if file_path:
            try:
                project = self.collect_all_data()
                data = asdict(project)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.statusBar().showMessage(f"Saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _open_project_json(self):
        """Fallback: لود JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._load_project_from_dict(data)
                self.statusBar().showMessage(f"Loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _load_project_from_dict(self, data: dict):
        """لود پروژه از dict به GUI"""
        try:
            from presets_module import load_project_into_gui
            from main import (
                WellProject, CompanyInfo, WellGeneralInfo,
                FormationTop, HazardEntry, CasingDesign,
                CementDesign, BHADesign, MudProgram,
                DirectionalPlan, BOPStack, WellControlData,
                RigSpecification, DrillingParameters, TimeEstimate
            )

            # Reconstruct WellProject from dict
            project = WellProject()

            # Company Info
            ci_data = data.get('company_info', {})
            project.company_info = CompanyInfo(**{
                k: v for k, v in ci_data.items()
                if k in CompanyInfo.__dataclass_fields__
            })

            # Well Info
            wi_data = data.get('well_info', {})
            project.well_info = WellGeneralInfo(**{
                k: v for k, v in wi_data.items()
                if k in WellGeneralInfo.__dataclass_fields__
            })

            # Formation Tops
            for ft_data in data.get('formation_tops', []):
                project.formation_tops.append(FormationTop(**{
                    k: v for k, v in ft_data.items()
                    if k in FormationTop.__dataclass_fields__
                }))

            # Hazards
            for h_data in data.get('hazards', []):
                project.hazards.append(HazardEntry(**{
                    k: v for k, v in h_data.items()
                    if k in HazardEntry.__dataclass_fields__
                }))

            # Casing Design
            for cd_data in data.get('casing_design', []):
                project.casing_design.append(CasingDesign(**{
                    k: v for k, v in cd_data.items()
                    if k in CasingDesign.__dataclass_fields__
                }))

            # Cement Design
            for cm_data in data.get('cement_design', []):
                project.cement_design.append(CementDesign(**{
                    k: v for k, v in cm_data.items()
                    if k in CementDesign.__dataclass_fields__
                }))

            # BHA
            for bha_data in data.get('bha_designs', []):
                filtered = {k: v for k, v in bha_data.items()
                           if k in BHADesign.__dataclass_fields__
                           and k != 'components'}
                project.bha_designs.append(BHADesign(**filtered))

            # Mud
            for mud_data in data.get('mud_programs', []):
                project.mud_programs.append(MudProgram(**{
                    k: v for k, v in mud_data.items()
                    if k in MudProgram.__dataclass_fields__
                }))

            # Directional
            dp_data = data.get('directional_plan', {})
            filtered_dp = {k: v for k, v in dp_data.items()
                          if k in DirectionalPlan.__dataclass_fields__}
            project.directional_plan = DirectionalPlan(**filtered_dp)

            # BOP
            bop_data = data.get('bop_stack', {})
            project.bop_stack = BOPStack(**{
                k: v for k, v in bop_data.items()
                if k in BOPStack.__dataclass_fields__
            })

            # Well Control
            wc_data = data.get('well_control', {})
            project.well_control = WellControlData(**{
                k: v for k, v in wc_data.items()
                if k in WellControlData.__dataclass_fields__
            })

            # Rig Spec
            rs_data = data.get('rig_spec', {})
            project.rig_spec = RigSpecification(**{
                k: v for k, v in rs_data.items()
                if k in RigSpecification.__dataclass_fields__
            })

            # Drilling Parameters
            for dp_data in data.get('drilling_parameters', []):
                project.drilling_parameters.append(DrillingParameters(**{
                    k: v for k, v in dp_data.items()
                    if k in DrillingParameters.__dataclass_fields__
                }))

            # Time Estimates
            for te_data in data.get('time_estimates', []):
                project.time_estimates.append(TimeEstimate(**{
                    k: v for k, v in te_data.items()
                    if k in TimeEstimate.__dataclass_fields__
                }))

            # Load into GUI
            load_project_into_gui(self, project)

        except Exception as e:
            import traceback
            QMessageBox.warning(
                self, "Load Warning",
                f"Project loaded with some issues:\n{str(e)}")
                
    def validate_data(self):
        """اعتبارسنجی داده‌ها"""
        project = self.collect_all_data()
        issues = []

        if not project.company_info.well_name:
            issues.append("⚠️ Well Name is empty")
        if not project.company_info.operator_name:
            issues.append("⚠️ Operator Name is empty")
        if project.well_info.total_depth_md <= 0:
            issues.append("⚠️ Total Depth (MD) is not set")
        if not project.formation_tops:
            issues.append("⚠️ No formation tops defined")
        if not project.casing_design:
            issues.append("⚠️ No casing design defined")
        if not project.mud_programs:
            issues.append("⚠️ No mud program defined")
        if not project.bha_designs:
            issues.append("⚠️ No BHA design defined")
        if not project.cement_design:
            issues.append("⚠️ No cement design defined")
        if project.bop_stack.working_pressure <= 0:
            issues.append("⚠️ BOP working pressure not set")

        # Check casing design factors
        for cd in project.casing_design:
            if cd.min_design_factor_burst < 1.0:
                issues.append(
                    f"⚠️ {cd.section_name}: Burst DF < 1.0")
            if cd.min_design_factor_collapse < 1.0:
                issues.append(
                    f"⚠️ {cd.section_name}: Collapse DF < 1.0")

        if issues:
            QMessageBox.warning(
                self, "Validation Issues",
                "The following issues were found:\n\n" + "\n".join(issues)
            )
        else:
            QMessageBox.information(
                self, "Validation",
                "✅ All required data appears to be filled correctly!"
            )

    def preview_document(self):
        """پیش‌نمایش واقعی سند از داده‌های فعلی"""
        try:
            project = self.collect_all_data()
            dialog = DocumentPreviewDialog(project, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Preview Error", str(e))


    def _quick_load_preset(self, preset_key: str):
        """بارگذاری سریع پریست — پیاده‌سازی تمیز با نمونه واقعی دیالوگ"""
        try:
            from presets_module import PresetSelectorDialog, load_project_into_gui

            dialog = PresetSelectorDialog(self)
            presets = dialog.presets
            dialog.deleteLater()

            if preset_key in presets:
                project = presets[preset_key]['generator']()
                load_project_into_gui(self, project, show_message=False)
                self.project = project
                self.statusBar().showMessage(
                    f"✅ Preset loaded: {presets[preset_key]['name']}")
                self.open_tab("company")
            else:
                QMessageBox.warning(
                    self, "Not Found",
                    f"Preset '{preset_key}' not found.\n\n"
                    f"Available: {', '.join(presets.keys())}"
                )

        except Exception as e:
            import traceback
            QMessageBox.critical(
                self, "Error",
                f"Error loading preset:\n{str(e)}\n\n"
                f"Use: Templates → Professional Well Templates..."
            )
            
    def show_about(self):
        QMessageBox.about(
            self, "About",
            "<h2>Drilling Program Generator Pro v3.1</h2>"
            "<p><b>Professional Drilling Program & Procedure Generator</b></p>"
            "<p>Integrated modules: Risk Analyzer • Engineering Tools • "
            "Master Programs • Procedures Library • Templates</p>"
            "<p>Based on industry standards:</p>"
            "<ul>"
            "<li>API RP 5C3, API RP 10B, API RP 13B</li>"
            "<li>IADC/SPE Drilling Practices</li>"
            "<li>Shell DEP Standards</li>"
            "<li>Saudi Aramco SAES</li>"
            "<li>BP GP Standards</li>"
            "<li>ISO 10400, ISO 10426</li>"
            "<li>NORSOK D-010</li>"
            "<li>API RP 53, API RP 59</li>"
            "</ul>"
            "<p>© 2024 - Professional Drilling Software</p>"
        )

    def show_standards(self):
        QMessageBox.information(
            self, "Standards Reference",
            "<h3>Referenced Standards & Guidelines</h3>"
            "<p><b>Casing Design:</b></p>"
            "<ul>"
            "<li>API 5CT - Casing & Tubing Specification</li>"
            "<li>API RP 5C3 - Casing Design</li>"
            "<li>ISO 10400 - Petroleum Casing Design</li>"
            "</ul>"
            "<p><b>Cementing:</b></p>"
            "<ul>"
            "<li>API RP 10B - Cement Testing</li>"
            "<li>API Spec 10A - Well Cements</li>"
            "<li>ISO 10426 - Well Cement Testing</li>"
            "</ul>"
            "<p><b>Drilling Fluids:</b></p>"
            "<ul>"
            "<li>API RP 13B - Drilling Fluid Testing</li>"
            "<li>API RP 13D - Rheology & Hydraulics</li>"
            "</ul>"
            "<p><b>Well Control:</b></p>"
            "<ul>"
            "<li>API RP 53 - BOP Equipment</li>"
            "<li>API RP 59 - Well Control</li>"
            "<li>IADC Well Control Manual</li>"
            "<li>NORSOK D-010 Well Integrity</li>"
            "</ul>"
            "<p><b>Directional Drilling:</b></p>"
            "<ul>"
            "<li>SPE/IADC Directional Drilling Guidelines</li>"
            "<li>ISCWSA Error Models</li>"
            "</ul>"
        )

    def load_template(self, template_name):
        """بارگذاری قالب"""
        if template_name == "me_dev":
            self.tab_formation.load_sample_me()
            self.tab_casing.load_sample()
            self.tab_mud.load_sample()
            self.tab_bha.load_sample_bha()
            self.tab_cement.load_sample()
            self.tab_time.load_sample()
            self.tab_time.load_sample_eval()
        elif template_name == "offshore_exp":
            self.tab_formation.load_sample_ns()
        elif template_name == "hpht":
            self.tab_formation.load_sample_ns()
        elif template_name == "horizontal":
            self.tab_formation.load_sample_gom()
        self.statusBar().showMessage(f"Template loaded: {template_name}")
