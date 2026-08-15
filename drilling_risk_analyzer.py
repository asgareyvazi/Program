#!/usr/bin/env python3
"""
Drilling Risk Analysis & Contingency Planning System
=====================================================
A production-ready desktop application for drilling and workover operation
risk analysis and contingency planning.

Author: Senior Drilling Engineer & Python Developer
License: MIT
"""

import sys
import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QComboBox, QLineEdit, QPushButton, QProgressBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QMessageBox, QSplitter, QFrame, QGroupBox, QSizePolicy, QDialog,
    QDialogButtonBox, QFormLayout, QSpinBox
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QColor, QFont, QIcon, QPalette, QBrush

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# =============================================================================
# DATA MODELS
# =============================================================================

class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


SEVERITY_COLORS = {
    RiskLevel.CRITICAL: QColor(220, 53, 69),
    RiskLevel.HIGH: QColor(255, 140, 0),
    RiskLevel.MEDIUM: QColor(255, 193, 7),
    RiskLevel.LOW: QColor(40, 167, 69),
}

SEVERITY_ORDER = {
    RiskLevel.CRITICAL: 0,
    RiskLevel.HIGH: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.LOW: 3,
}


@dataclass
class ContingencyStep:
    """A single contingency action for a risk scenario."""
    action: str
    priority: int  # 1 = highest
    duration_hours: float
    success_probability: float  # 0.0 to 1.0
    estimated_cost_usd: float
    resources_needed: List[str] = field(default_factory=list)
    key_notes: str = ""


@dataclass
class OperationRisk:
    """A risk scenario linked to a drilling/workover operation."""
    problem: str
    category: str
    severity: RiskLevel
    probability: float  # 0.0 to 1.0
    npt_hours: float
    early_warning_signs: List[str] = field(default_factory=list)
    root_causes: List[str] = field(default_factory=list)
    contingency_plans: List[ContingencyStep] = field(default_factory=list)
    related_operations: List[str] = field(default_factory=list)


@dataclass
class ForgottenItem:
    """A best-practice item that may be overlooked."""
    description: str
    related_operations: List[str]
    severity: RiskLevel
    recommended_action: str
    reference: str = ""


# =============================================================================
# KNOWLEDGE BASE — 60+ Real Drilling Risk Scenarios
# =============================================================================

def build_risk_database() -> List[OperationRisk]:
    """Build the comprehensive risk knowledge base with 60+ scenarios."""
    risks = [
        # =====================================================================
        # DRILLING RISKS (1-15)
        # =====================================================================
        OperationRisk(
            problem="Kick / Well Control Event",
            category="Well Control",
            severity=RiskLevel.CRITICAL,
            probability=0.08,
            npt_hours=48,
            early_warning_signs=[
                "Increase in return flow rate",
                "Pit volume gain",
                "Drilling break (sudden increase in ROP)",
                "Reduction in pump pressure",
                "Gas cut mud returns"
            ],
            root_causes=[
                "Insufficient mud weight",
                "Swabbing while tripping",
                "Unexpected high-pressure zone",
                "Lost circulation leading to reduced hydrostatic",
                "Poor pore pressure prediction"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Shut in well using hard shut-in procedure; read SIDPP and SICP",
                    priority=1, duration_hours=0.5, success_probability=0.95,
                    estimated_cost_usd=5000,
                    resources_needed=["BOP", "Choke manifold", "Well control trained crew"],
                    key_notes="Follow API RP 53 well control procedures"
                ),
                ContingencyStep(
                    action="Circulate kick out using Driller's Method or Wait & Weight",
                    priority=2, duration_hours=8, success_probability=0.90,
                    estimated_cost_usd=25000,
                    resources_needed=["Kill weight mud", "Choke operator", "Monitoring equipment"],
                    key_notes="Maintain constant BHP throughout circulation"
                ),
                ContingencyStep(
                    action="Bullhead kill fluid if unable to circulate",
                    priority=3, duration_hours=4, success_probability=0.70,
                    estimated_cost_usd=50000,
                    resources_needed=["High pressure pumps", "Kill fluid volume"],
                    key_notes="Last resort; risk of underground blowout"
                ),
            ],
            related_operations=["drilling", "tripping"]
        ),
        OperationRisk(
            problem="Lost Circulation (Partial)",
            category="Drilling Fluids",
            severity=RiskLevel.HIGH,
            probability=0.20,
            npt_hours=12,
            early_warning_signs=[
                "Gradual decrease in return flow",
                "Pit level dropping",
                "Decrease in ECD",
                "Prior losses in offset wells"
            ],
            root_causes=[
                "Exceeding fracture gradient",
                "Natural fractures or vugs",
                "High ECD from excessive flow rate or mud weight",
                "Surge pressure during tripping"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Reduce mud weight and flow rate; spot LCM pill",
                    priority=1, duration_hours=4, success_probability=0.75,
                    estimated_cost_usd=15000,
                    resources_needed=["LCM materials (nut plug, mica, cellulose)", "Mixing hopper"],
                    key_notes="Use graded LCM blend; monitor returns closely"
                ),
                ContingencyStep(
                    action="Pump cement squeeze at loss zone",
                    priority=2, duration_hours=12, success_probability=0.80,
                    estimated_cost_usd=60000,
                    resources_needed=["Cement unit", "Cement slurry", "Squeeze packer"],
                    key_notes="May require multiple squeezes"
                ),
            ],
            related_operations=["drilling", "cementing"]
        ),
        OperationRisk(
            problem="Total Lost Circulation",
            category="Drilling Fluids",
            severity=RiskLevel.CRITICAL,
            probability=0.08,
            npt_hours=36,
            early_warning_signs=[
                "Complete loss of returns",
                "Rapid pit volume decrease",
                "Wellbore instability signs"
            ],
            root_causes=[
                "Drilling into cavernous formation",
                "Exceeding fracture gradient significantly",
                "Pre-existing faults"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Pump high-concentration LCM pill and wait on cement",
                    priority=1, duration_hours=8, success_probability=0.50,
                    estimated_cost_usd=30000,
                    resources_needed=["Large volume LCM", "Cement unit"],
                    key_notes="Monitor annular level to prevent dry pipe sticking"
                ),
                ContingencyStep(
                    action="Drill ahead with managed pressure drilling (MPD) if available",
                    priority=2, duration_hours=24, success_probability=0.70,
                    estimated_cost_usd=150000,
                    resources_needed=["MPD equipment", "RCD", "Back-pressure pump"],
                    key_notes="Requires MPD equipment on site"
                ),
                ContingencyStep(
                    action="Set a cement plug and sidetrack",
                    priority=3, duration_hours=72, success_probability=0.85,
                    estimated_cost_usd=500000,
                    resources_needed=["Cement", "Whipstock or cement plug"],
                    key_notes="Last resort; significant NPT and cost"
                ),
            ],
            related_operations=["drilling"]
        ),
        OperationRisk(
            problem="Differential Sticking",
            category="Stuck Pipe",
            severity=RiskLevel.HIGH,
            probability=0.15,
            npt_hours=24,
            early_warning_signs=[
                "Inability to move pipe up/down but free to rotate",
                "High overbalance across permeable zone",
                "Thick filter cake buildup",
                "Stationary pipe against permeable formation"
            ],
            root_causes=[
                "Excessive overbalance pressure",
                "Thick filter cake (poor mud properties)",
                "Stationary pipe in open hole",
                "Poor hole cleaning"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Apply maximum allowable torque and jarring; reduce mud weight if safe",
                    priority=1, duration_hours=6, success_probability=0.50,
                    estimated_cost_usd=10000,
                    resources_needed=["Jars in BHA", "Torque monitoring"],
                    key_notes="Do not exceed pipe body yield; jar in both directions"
                ),
                ContingencyStep(
                    action="Spot oil/diesel-based spotting fluid across stuck zone",
                    priority=2, duration_hours=12, success_probability=0.65,
                    estimated_cost_usd=25000,
                    resources_needed=["Spotting fluid (diesel/oil based)", "Coiled tubing if available"],
                    key_notes="Allow soak time of 8-12 hours minimum"
                ),
                ContingencyStep(
                    action="Back-off above stuck point; run fishing assembly",
                    priority=3, duration_hours=36, success_probability=0.70,
                    estimated_cost_usd=150000,
                    resources_needed=["Free point indicator", "Back-off tools", "Fishing BHA"],
                    key_notes="Determine free point before back-off"
                ),
            ],
            related_operations=["drilling", "logging"]
        ),
        OperationRisk(
            problem="Mechanical Sticking (Pack-off / Bridge)",
            category="Stuck Pipe",
            severity=RiskLevel.HIGH,
            probability=0.12,
            npt_hours=18,
            early_warning_signs=[
                "Increase in drag and torque trends",
                "Tight spots while tripping",
                "Poor hole cleaning indicators (cuttings at shakers)",
                "Overpull on connections"
            ],
            root_causes=[
                "Poor hole cleaning",
                "Reactive shale / swelling",
                "Ledges and key seats",
                "Cuttings accumulation in washouts"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Work pipe with maximum allowable parameters; increase flow rate and rotation",
                    priority=1, duration_hours=4, success_probability=0.60,
                    estimated_cost_usd=5000,
                    resources_needed=["Rig pumps at max rate", "Top drive"],
                    key_notes="Pump high-viscosity sweeps"
                ),
                ContingencyStep(
                    action="Jar and work pipe; pump viscous sweeps to clean hole",
                    priority=2, duration_hours=8, success_probability=0.70,
                    estimated_cost_usd=15000,
                    resources_needed=["Jars", "Hi-vis sweep material"],
                    key_notes="Monitor returns for cuttings volume"
                ),
            ],
            related_operations=["drilling", "tripping"]
        ),
        OperationRisk(
            problem="Wellbore Instability / Hole Collapse",
            category="Geomechanics",
            severity=RiskLevel.HIGH,
            probability=0.15,
            npt_hours=24,
            early_warning_signs=[
                "Cavings at shaker (splintery or angular)",
                "Increased torque and drag",
                "Tight hole / overpull",
                "Hole fill on connections"
            ],
            root_causes=[
                "Insufficient mud weight (below collapse pressure)",
                "Reactive shales with water-based mud",
                "Time-dependent shale failure",
                "Tectonic stresses",
                "Improper well trajectory"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Increase mud weight incrementally; monitor for losses",
                    priority=1, duration_hours=4, success_probability=0.70,
                    estimated_cost_usd=20000,
                    resources_needed=["Barite", "Mud engineering support"],
                    key_notes="Stay within mud weight window"
                ),
                ContingencyStep(
                    action="Switch to inhibitive mud system (KCl, oil-based)",
                    priority=2, duration_hours=12, success_probability=0.80,
                    estimated_cost_usd=80000,
                    resources_needed=["OBM or inhibitive WBM chemicals"],
                    key_notes="Consider environmental regulations"
                ),
            ],
            related_operations=["drilling"]
        ),
        OperationRisk(
            problem="Drill String Washout",
            category="Equipment Failure",
            severity=RiskLevel.MEDIUM,
            probability=0.10,
            npt_hours=8,
            early_warning_signs=[
                "Gradual decrease in standpipe pressure",
                "Increase in pump strokes for same pressure",
                "Erratic WOB/torque readings"
            ],
            root_causes=[
                "Fatigue failure at tool joint connections",
                "Corrosion / erosion of drill pipe",
                "Improper make-up torque",
                "Damaged threads"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="POOH to locate and replace washed out joint",
                    priority=1, duration_hours=8, success_probability=0.95,
                    estimated_cost_usd=15000,
                    resources_needed=["Spare drill pipe", "Pipe inspection"],
                    key_notes="Inspect pipe during trip; mark suspect joints"
                ),
            ],
            related_operations=["drilling"]
        ),
        OperationRisk(
            problem="Twist-off / Drill String Failure",
            category="Equipment Failure",
            severity=RiskLevel.CRITICAL,
            probability=0.05,
            npt_hours=48,
            early_warning_signs=[
                "Erratic torque fluctuations",
                "Metal returns at shaker",
                "Sudden drop in weight and torque",
                "Prior washout indicators"
            ],
            root_causes=[
                "Fatigue from cyclic loading",
                "Severe washout progressed to twist-off",
                "Dogleg severity causing fatigue",
                "Corrosion (H2S, CO2)",
                "Excessive torque/overpull"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Recover broken drill string with overshot / fishing tools",
                    priority=1, duration_hours=24, success_probability=0.75,
                    estimated_cost_usd=100000,
                    resources_needed=["Fishing tools (overshot, bumper sub, jars)", "Fishing engineer"],
                    key_notes="Get fish dimensions before RIH fishing assembly"
                ),
                ContingencyStep(
                    action="Mill over fish and recover",
                    priority=2, duration_hours=48, success_probability=0.60,
                    estimated_cost_usd=200000,
                    resources_needed=["Mill, wash pipe", "Fishing engineer"],
                    key_notes="If overshot engagement fails"
                ),
                ContingencyStep(
                    action="Sidetrack around fish",
                    priority=3, duration_hours=96, success_probability=0.90,
                    estimated_cost_usd=500000,
                    resources_needed=["Cement", "Whipstock", "New BHA"],
                    key_notes="Last resort after fishing attempts exhausted"
                ),
            ],
            related_operations=["drilling", "fishing"]
        ),
        OperationRisk(
            problem="Bit Damage / Bit Balling",
            category="Bit Performance",
            severity=RiskLevel.MEDIUM,
            probability=0.18,
            npt_hours=10,
            early_warning_signs=[
                "Decrease in ROP with same parameters",
                "Increased torque fluctuation",
                "High MSE values",
                "Gumbo at shakers (bit balling)"
            ],
            root_causes=[
                "Drilling through abrasive formation",
                "Improper bit selection",
                "Reactive clay balling on PDC cutters",
                "Excessive WOB causing cutter damage"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Trip out to change bit; select appropriate bit for formation",
                    priority=1, duration_hours=10, success_probability=0.95,
                    estimated_cost_usd=50000,
                    resources_needed=["Replacement bit", "Trip time"],
                    key_notes="Grade bit using IADC dull grading system"
                ),
                ContingencyStep(
                    action="Adjust drilling parameters (WOB, RPM, flow rate) to mitigate balling",
                    priority=1, duration_hours=1, success_probability=0.50,
                    estimated_cost_usd=0,
                    resources_needed=["Drilling optimization engineer"],
                    key_notes="Try before tripping; use anti-balling agents"
                ),
            ],
            related_operations=["drilling"]
        ),
        OperationRisk(
            problem="Directional Drilling Difficulty / Trajectory Deviation",
            category="Directional",
            severity=RiskLevel.MEDIUM,
            probability=0.15,
            npt_hours=12,
            early_warning_signs=[
                "Surveys showing deviation from plan",
                "Difficulty building/dropping angle",
                "Slide drilling inefficiency"
            ],
            root_causes=[
                "Formation tendencies (dip, anisotropy)",
                "BHA design not suitable",
                "MWD/RSS tool malfunction",
                "Motor yield failure"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Modify BHA configuration; adjust bent housing angle or stabilizer placement",
                    priority=1, duration_hours=10, success_probability=0.80,
                    estimated_cost_usd=30000,
                    resources_needed=["Alternative BHA components", "Directional driller"],
                    key_notes="Review anti-collision before changing trajectory"
                ),
                ContingencyStep(
                    action="Set cement plug and sidetrack to correct trajectory",
                    priority=2, duration_hours=48, success_probability=0.85,
                    estimated_cost_usd=200000,
                    resources_needed=["Cement", "Sidetrack BHA"],
                    key_notes="High cost option; use only if correction not feasible"
                ),
            ],
            related_operations=["drilling"]
        ),
        OperationRisk(
            problem="Downhole Tool Failure (MWD/LWD/RSS)",
            category="Equipment Failure",
            severity=RiskLevel.MEDIUM,
            probability=0.12,
            npt_hours=12,
            early_warning_signs=[
                "Loss of MWD signal / telemetry",
                "Erratic survey data",
                "Tool diagnostics showing anomalies"
            ],
            root_causes=[
                "Electronic component failure due to temperature",
                "Vibration / shock damage",
                "Battery depletion",
                "Mud pulse interference"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Attempt surface reboot / diagnostic; adjust flow for mud pulse",
                    priority=1, duration_hours=2, success_probability=0.40,
                    estimated_cost_usd=0,
                    resources_needed=["MWD engineer"],
                    key_notes="Try cycling pumps; check surface equipment first"
                ),
                ContingencyStep(
                    action="POOH and replace MWD/LWD tools",
                    priority=2, duration_hours=12, success_probability=0.95,
                    estimated_cost_usd=50000,
                    resources_needed=["Backup MWD/LWD tools"],
                    key_notes="Ensure backup tools tested on surface before RIH"
                ),
            ],
            related_operations=["drilling"]
        ),
        OperationRisk(
            problem="Surge/Swab Pressure Related Kick or Losses",
            category="Well Control",
            severity=RiskLevel.HIGH,
            probability=0.10,
            npt_hours=12,
            early_warning_signs=[
                "Flow check positive after pulling pipe",
                "Losses observed when running in hole fast",
                "Narrow mud weight window"
            ],
            root_causes=[
                "Excessive trip speed",
                "Balled bit increasing surge",
                "Tight annular clearance",
                "Gelled mud"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Control trip speed; use trip schedule; break gel before tripping",
                    priority=1, duration_hours=1, success_probability=0.85,
                    estimated_cost_usd=0,
                    resources_needed=["Trip speed monitoring"],
                    key_notes="Maximum 3 stands/hr in critical zones"
                ),
                ContingencyStep(
                    action="Perform flow checks; if kick confirmed, shut in and kill well",
                    priority=2, duration_hours=8, success_probability=0.90,
                    estimated_cost_usd=25000,
                    resources_needed=["BOP", "Kill weight mud"],
                    key_notes="Follow well control procedures"
                ),
            ],
            related_operations=["tripping", "casing_running"]
        ),
        OperationRisk(
            problem="H2S Influx / Toxic Gas Exposure",
            category="HSE",
            severity=RiskLevel.CRITICAL,
            probability=0.05,
            npt_hours=24,
            early_warning_signs=[
                "H2S detector alarms",
                "Rotten egg smell at low concentrations",
                "Drill pipe corrosion indicators",
                "Prior H2S presence in offset wells"
            ],
            root_causes=[
                "Drilling into H2S bearing zone",
                "Thermal decomposition of drilling additives",
                "Bacterial action on sulfates"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Activate H2S contingency plan; muster crew at safe briefing area",
                    priority=1, duration_hours=0.5, success_probability=0.95,
                    estimated_cost_usd=5000,
                    resources_needed=["SCBA equipment", "Wind socks", "H2S monitors"],
                    key_notes="Follow H2S safety plan per API RP 49"
                ),
                ContingencyStep(
                    action="Treat mud with zinc-based scavenger; increase pH",
                    priority=2, duration_hours=4, success_probability=0.85,
                    estimated_cost_usd=20000,
                    resources_needed=["Zinc carbonate/oxide", "Caustic soda"],
                    key_notes="Maintain pH > 10 to keep H2S ionized in mud"
                ),
            ],
            related_operations=["drilling", "well_testing", "completion"]
        ),
        OperationRisk(
            problem="Shallow Gas Kick",
            category="Well Control",
            severity=RiskLevel.CRITICAL,
            probability=0.06,
            npt_hours=24,
            early_warning_signs=[
                "Gas bubbles at surface around conductor",
                "Rapid pit gain",
                "Seismic anomalies in shallow section"
            ],
            root_causes=[
                "Shallow biogenic gas pockets",
                "Insufficient conductor shoe depth",
                "No diverter system ready"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Activate diverter system; divert flow away from rig floor",
                    priority=1, duration_hours=0.25, success_probability=0.85,
                    estimated_cost_usd=10000,
                    resources_needed=["Diverter system", "Diverter line"],
                    key_notes="NEVER shut in on shallow gas; always divert"
                ),
                ContingencyStep(
                    action="Pump kill mud at maximum rate through drillstring",
                    priority=2, duration_hours=2, success_probability=0.70,
                    estimated_cost_usd=15000,
                    resources_needed=["Heavy mud ready", "All pumps"],
                    key_notes="Dynamic kill using maximum flow rate"
                ),
            ],
            related_operations=["drilling"]
        ),
        OperationRisk(
            problem="High Torque and Drag",
            category="Drilling Mechanics",
            severity=RiskLevel.MEDIUM,
            probability=0.20,
            npt_hours=6,
            early_warning_signs=[
                "Torque approaching limits",
                "Excessive drag on connections",
                "Difficulty reaching bottom after connections",
                "Increasing trend in T&D charts"
            ],
            root_causes=[
                "Hole angle and dogleg severity",
                "Poor hole cleaning (cuttings bed)",
                "Micro-doglegs from slide drilling",
                "Tight formation / undergauge hole"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Increase rotation and flow rate; pump sweeps; optimize mud lubricity",
                    priority=1, duration_hours=2, success_probability=0.70,
                    estimated_cost_usd=5000,
                    resources_needed=["Lubricant additives", "Sweep material"],
                    key_notes="Compare actual vs. modeled T&D"
                ),
                ContingencyStep(
                    action="Short trip to condition hole; ream tight spots",
                    priority=2, duration_hours=6, success_probability=0.80,
                    estimated_cost_usd=10000,
                    resources_needed=["Trip time"],
                    key_notes="Ream carefully to avoid keyseating"
                ),
            ],
            related_operations=["drilling", "tripping", "casing_running"]
        ),
        # =====================================================================
        # TRIPPING RISKS (16-22)
        # =====================================================================
        OperationRisk(
            problem="Swabbing Kick During POOH",
            category="Well Control",
            severity=RiskLevel.HIGH,
            probability=0.10,
            npt_hours=12,
            early_warning_signs=[
                "Positive flow check after pulling stands",
                "Trip tank not filling properly",
                "Hole not taking proper fill volume"
            ],
            root_causes=[
                "Pulling pipe too fast",
                "Balled bit increasing swab pressure",
                "Gelled mud not broken before tripping",
                "Tight annular clearance (stabilizers)"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Perform flow check; if positive, shut in and circulate bottoms-up",
                    priority=1, duration_hours=4, success_probability=0.90,
                    estimated_cost_usd=10000,
                    resources_needed=["Trip tank monitoring", "BOP"],
                    key_notes="Monitor trip tank volumes rigorously"
                ),
                ContingencyStep(
                    action="Control tripping speed; use trip schedule for critical sections",
                    priority=1, duration_hours=0, success_probability=0.95,
                    estimated_cost_usd=0,
                    resources_needed=["Trip speed monitoring system"],
                    key_notes="Prevention: max 3 stands/min in critical zones"
                ),
            ],
            related_operations=["tripping"]
        ),
        OperationRisk(
            problem="Stuck Pipe While Tripping (Key Seat)",
            category="Stuck Pipe",
            severity=RiskLevel.HIGH,
            probability=0.10,
            npt_hours=18,
            early_warning_signs=[
                "Sticking at same depth repeatedly",
                "Can lower but cannot pull through zone",
                "High dogleg severity areas",
                "Pipe hangs up at tool joints"
            ],
            root_causes=[
                "Severe dogleg creating groove in formation",
                "Running large OD tool through key seat",
                "Formation type (firm/medium formations)"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Work pipe down; attempt to rotate through key seat",
                    priority=1, duration_hours=4, success_probability=0.60,
                    estimated_cost_usd=5000,
                    resources_needed=["Top drive rotation"],
                    key_notes="Never pull with high overpull; risk of twist-off"
                ),
                ContingencyStep(
                    action="Ream through key seat with key seat wiper on next trip",
                    priority=2, duration_hours=8, success_probability=0.80,
                    estimated_cost_usd=15000,
                    resources_needed=["Key seat wiper", "Reaming time"],
                    key_notes="Plan BHA to include key seat wiper"
                ),
            ],
            related_operations=["tripping"]
        ),
        OperationRisk(
            problem="Dropped Object in Wellbore During Trip",
            category="Equipment Failure",
            severity=RiskLevel.HIGH,
            probability=0.05,
            npt_hours=24,
            early_warning_signs=[
                "Unusual noise / vibration at surface",
                "Inability to reach bottom after trip",
                "Obstruction felt at certain depth"
            ],
            root_causes=[
                "Improper handling of pipe / tools",
                "Equipment failure (slips, elevators)",
                "Loose components in BHA"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Run junk basket or magnet to recover small items",
                    priority=1, duration_hours=12, success_probability=0.60,
                    estimated_cost_usd=30000,
                    resources_needed=["Junk basket", "Fishing magnet", "Impression block"],
                    key_notes="Run impression block first to identify fish"
                ),
                ContingencyStep(
                    action="Mill junk on bottom if cannot be fished",
                    priority=2, duration_hours=24, success_probability=0.70,
                    estimated_cost_usd=60000,
                    resources_needed=["Junk mill", "Junk basket sub"],
                    key_notes="Circulate debris; use junk sub above bit"
                ),
            ],
            related_operations=["tripping", "fishing"]
        ),
        OperationRisk(
            problem="BHA / Stabilizer Hang-up on Casing Shoe",
            category="Tripping",
            severity=RiskLevel.MEDIUM,
            probability=0.12,
            npt_hours=4,
            early_warning_signs=[
                "Resistance at casing shoe depth while RIH",
                "Need to apply weight to pass shoe"
            ],
            root_causes=[
                "Casing shoe debris / cement",
                "Undergauge rat hole below shoe",
                "Misaligned casing shoe track"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Ream through shoe track slowly with rotation and circulation",
                    priority=1, duration_hours=2, success_probability=0.90,
                    estimated_cost_usd=3000,
                    resources_needed=["Top drive rotation"],
                    key_notes="Be cautious of shoe integrity"
                ),
            ],
            related_operations=["tripping", "drilling"]
        ),
        OperationRisk(
            problem="Pipe Light / Unable to Run to Bottom",
            category="Tripping",
            severity=RiskLevel.MEDIUM,
            probability=0.08,
            npt_hours=6,
            early_warning_signs=[
                "Increasing set-down weight needed",
                "Buckling indicators in deviated wells",
                "Cannot reach target depth"
            ],
            root_causes=[
                "Friction in high-angle wells",
                "Cuttings bed in horizontal section",
                "Insufficient pipe weight"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Add heavy-weight drill pipe; circulate and rotate while RIH",
                    priority=1, duration_hours=4, success_probability=0.75,
                    estimated_cost_usd=10000,
                    resources_needed=["HWDP", "Top drive"],
                    key_notes="Use T&D model to verify buckling limits"
                ),
            ],
            related_operations=["tripping"]
        ),
        OperationRisk(
            problem="Hole Fill / Bridge After Trip",
            category="Hole Condition",
            severity=RiskLevel.MEDIUM,
            probability=0.15,
            npt_hours=6,
            early_warning_signs=[
                "Fill on bottom after trip",
                "Cannot reach previous TD",
                "Tight hole on RIH near TD"
            ],
            root_causes=[
                "Poor hole cleaning before POOH",
                "Unstable formation collapse",
                "Settling of cuttings during trip"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Ream to bottom; circulate bottoms-up with high flow and rotation",
                    priority=1, duration_hours=4, success_probability=0.85,
                    estimated_cost_usd=5000,
                    resources_needed=["Top drive", "Rig pumps"],
                    key_notes="Pump sweeps; clean hole before next trip"
                ),
            ],
            related_operations=["tripping", "drilling"]
        ),
        OperationRisk(
            problem="Slip Cuts on Drill Pipe",
            category="Equipment Damage",
            severity=RiskLevel.LOW,
            probability=0.15,
            npt_hours=2,
            early_warning_signs=[
                "Visible slip marks on pipe body",
                "Worn slip dies",
                "Pipe not properly seated in slips"
            ],
            root_causes=[
                "Worn slip inserts",
                "Improper slip engagement",
                "Excessive hanging weight on slips"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Inspect and replace worn slip dies; monitor pipe for deep cuts",
                    priority=1, duration_hours=2, success_probability=0.95,
                    estimated_cost_usd=2000,
                    resources_needed=["Replacement slip dies", "Pipe inspection"],
                    key_notes="Deep slip cuts can initiate fatigue cracks"
                ),
            ],
            related_operations=["tripping", "drilling"]
        ),
        # =====================================================================
        # CASING RUNNING RISKS (23-30)
        # =====================================================================
        OperationRisk(
            problem="Casing Stuck Off-Bottom",
            category="Casing Running",
            severity=RiskLevel.CRITICAL,
            probability=0.08,
            npt_hours=36,
            early_warning_signs=[
                "Increasing drag while running casing",
                "Casing cannot pass known tight spots",
                "Overpull required to move casing"
            ],
            root_causes=[
                "Inadequate hole cleaning before running casing",
                "Tight hole / undergauge sections",
                "Swelling shales",
                "Insufficient mud conditioning",
                "Lack of centralizers causing differential sticking"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Reciprocate and rotate casing (if connections allow); circulate and condition",
                    priority=1, duration_hours=8, success_probability=0.55,
                    estimated_cost_usd=20000,
                    resources_needed=["Casing running tool with rotation", "Rig pumps"],
                    key_notes="Only if casing connections are rated for rotation"
                ),
                ContingencyStep(
                    action="POOH casing; condition hole; rerun casing with reamer shoe",
                    priority=2, duration_hours=24, success_probability=0.80,
                    estimated_cost_usd=100000,
                    resources_needed=["Reamer shoe", "Casing running time", "Mud conditioning"],
                    key_notes="High risk of swab/surge; condition mud first"
                ),
                ContingencyStep(
                    action="Set casing at current depth and adjust cement program",
                    priority=3, duration_hours=4, success_probability=0.70,
                    estimated_cost_usd=30000,
                    resources_needed=["Modified cement program"],
                    key_notes="Verify setting depth provides adequate shoe strength"
                ),
            ],
            related_operations=["casing_running"]
        ),
        OperationRisk(
            problem="Casing Connection Cross-Threading / Damage",
            category="Casing Running",
            severity=RiskLevel.HIGH,
            probability=0.08,
            npt_hours=6,
            early_warning_signs=[
                "Irregular torque graph during make-up",
                "Unable to achieve target torque",
                "Thread compound contamination"
            ],
            root_causes=[
                "Misalignment during stabbing",
                "Dirty or damaged threads",
                "Improper make-up speed",
                "Wrong thread compound"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Lay down damaged joint; inspect and re-prep threads; continue with new joint",
                    priority=1, duration_hours=2, success_probability=0.95,
                    estimated_cost_usd=10000,
                    resources_needed=["Spare casing joint", "Thread inspection tools"],
                    key_notes="Clean and inspect all threads before stabbing"
                ),
            ],
            related_operations=["casing_running"]
        ),
        OperationRisk(
            problem="Casing Wear from Drill String Rotation",
            category="Casing Integrity",
            severity=RiskLevel.MEDIUM,
            probability=0.12,
            npt_hours=0,
            early_warning_signs=[
                "Casing wear log showing wall loss",
                "Metal filings in returns",
                "Extended drilling hours through casing window"
            ],
            root_causes=[
                "Extended drilling with rotation in cased hole",
                "Doglegs inside casing",
                "Abrasive drilling fluid",
                "Hard-facing on tool joints"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Run casing wear log; install casing protectors (non-rotating) at high DLS points",
                    priority=1, duration_hours=4, success_probability=0.80,
                    estimated_cost_usd=15000,
                    resources_needed=["Casing protectors", "Wear monitoring"],
                    key_notes="Plan wear budget during well design"
                ),
                ContingencyStep(
                    action="Patch casing with tie-back or liner if wear exceeds limits",
                    priority=2, duration_hours=48, success_probability=0.85,
                    estimated_cost_usd=300000,
                    resources_needed=["Casing patch / liner", "Cement"],
                    key_notes="Extreme case; plan for burst/collapse reduction"
                ),
            ],
            related_operations=["drilling", "casing_running"]
        ),
        OperationRisk(
            problem="Float Equipment Failure",
            category="Casing Running",
            severity=RiskLevel.HIGH,
            probability=0.08,
            npt_hours=12,
            early_warning_signs=[
                "Flow coming from casing shoe while running",
                "Cannot convert float / auto-fill equipment",
                "Unable to establish circulation through shoe"
            ],
            root_causes=[
                "Debris blocking float valve",
                "Float collar / shoe damaged during running",
                "Incorrect float equipment selection"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Pump to establish circulation; try to convert with ball/dart",
                    priority=1, duration_hours=2, success_probability=0.70,
                    estimated_cost_usd=5000,
                    resources_needed=["Ball/dart", "Rig pumps"],
                    key_notes="If auto-fill, pump at conversion rate"
                ),
                ContingencyStep(
                    action="Drill out float and recement if float fails to hold",
                    priority=2, duration_hours=12, success_probability=0.85,
                    estimated_cost_usd=40000,
                    resources_needed=["Drill-out BHA", "Cement"],
                    key_notes="Float failure affects cement integrity"
                ),
            ],
            related_operations=["casing_running", "cementing"]
        ),
        OperationRisk(
            problem="Casing Running in High Angle Well - Cannot Reach TD",
            category="Casing Running",
            severity=RiskLevel.HIGH,
            probability=0.10,
            npt_hours=24,
            early_warning_signs=[
                "Increasing drag while running casing",
                "Casing stalling at build/drop sections",
                "Modeled drag exceeding available casing weight"
            ],
            root_causes=[
                "High friction coefficient in wellbore",
                "Insufficient casing weight for push",
                "Inadequate centralizer program",
                "Poor hole condition"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Use casing flotation device (air chamber) to reduce drag",
                    priority=1, duration_hours=4, success_probability=0.75,
                    estimated_cost_usd=30000,
                    resources_needed=["Casing flotation device"],
                    key_notes="Plan during well design phase"
                ),
                ContingencyStep(
                    action="POOH; condition hole with wiper trip; rerun with liner instead",
                    priority=2, duration_hours=36, success_probability=0.80,
                    estimated_cost_usd=150000,
                    resources_needed=["Liner hanger", "Liner string"],
                    key_notes="Liner option reduces setting depth requirement"
                ),
            ],
            related_operations=["casing_running"]
        ),
        OperationRisk(
            problem="Casing Collapse During Cementing",
            category="Casing Integrity",
            severity=RiskLevel.CRITICAL,
            probability=0.03,
            npt_hours=72,
            early_warning_signs=[
                "Sudden loss of pump pressure during cement job",
                "Abnormal surface pressures",
                "Previous casing design near collapse limit"
            ],
            root_causes=[
                "High cement density exceeding casing collapse rating",
                "Evacuation of casing during lost circulation",
                "High external pressure from heavy annular fluid"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Review casing design for cement column; use lightweight cement if needed",
                    priority=1, duration_hours=2, success_probability=0.90,
                    estimated_cost_usd=10000,
                    resources_needed=["Lightweight cement (foam/nitrogen)", "Casing design review"],
                    key_notes="Prevention: verify collapse safety factor with full cement column"
                ),
            ],
            related_operations=["casing_running", "cementing"]
        ),
        OperationRisk(
            problem="Landing String / Running Tool Failure",
            category="Casing Running",
            severity=RiskLevel.MEDIUM,
            probability=0.06,
            npt_hours=8,
            early_warning_signs=[
                "Difficulty releasing running tool",
                "Excessive torque at surface",
                "Running tool activation issues"
            ],
            root_causes=[
                "Running tool malfunction",
                "Excessive weight on tool",
                "Debris contamination"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Follow tool-specific contingency (apply set-down weight, pressure activation)",
                    priority=1, duration_hours=4, success_probability=0.80,
                    estimated_cost_usd=5000,
                    resources_needed=["Running tool manual", "Service engineer"],
                    key_notes="Ensure backup release mechanism known before RIH"
                ),
            ],
            related_operations=["casing_running"]
        ),
        # =====================================================================
        # CEMENTING RISKS (31-37)
        # =====================================================================
        OperationRisk(
            problem="Poor Cement Bond / Channeling",
            category="Cementing",
            severity=RiskLevel.HIGH,
            probability=0.18,
            npt_hours=24,
            early_warning_signs=[
                "Cement bond log (CBL) showing poor bond",
                "Annular pressure after cementing (SAPB)",
                "Gas migration indicators",
                "Low cement returns"
            ],
            root_causes=[
                "Poor mud removal / inadequate spacer",
                "Eccentric casing (poor centralization)",
                "Insufficient contact time",
                "Free water in cement allowing channels",
                "Gas migration through cement during transition"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Perform remedial cement squeeze at poor bond intervals",
                    priority=1, duration_hours=12, success_probability=0.70,
                    estimated_cost_usd=50000,
                    resources_needed=["Squeeze packer", "Cement unit", "Perforating guns (if needed)"],
                    key_notes="May need multiple squeezes for full coverage"
                ),
                ContingencyStep(
                    action="Run cement evaluation log; plan targeted squeeze if isolated channels",
                    priority=2, duration_hours=8, success_probability=0.60,
                    estimated_cost_usd=30000,
                    resources_needed=["CBL/VDL logging tool"],
                    key_notes="Compare with baseline CBL at different times"
                ),
            ],
            related_operations=["cementing"]
        ),
        OperationRisk(
            problem="Cement Contamination by Mud",
            category="Cementing",
            severity=RiskLevel.MEDIUM,
            probability=0.12,
            npt_hours=8,
            early_warning_signs=[
                "Abnormal surface pressures during pumping",
                "Cement returns appear contaminated",
                "Unexpected thickening time changes"
            ],
            root_causes=[
                "Inadequate spacer volume / properties",
                "No wiper plugs used",
                "Mud not properly conditioned before cement",
                "Incompatible mud/spacer/cement systems"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Increase spacer volume; verify compatibility testing done pre-job",
                    priority=1, duration_hours=2, success_probability=0.85,
                    estimated_cost_usd=10000,
                    resources_needed=["Compatible spacer", "Lab testing"],
                    key_notes="Run spacer ahead of and behind cement"
                ),
            ],
            related_operations=["cementing"]
        ),
        OperationRisk(
            problem="Cement Not Setting / Retarded Cement",
            category="Cementing",
            severity=RiskLevel.HIGH,
            probability=0.05,
            npt_hours=24,
            early_warning_signs=[
                "No pressure increase after displacement",
                "Cannot test shoe after expected WOC time",
                "Temperature lower than expected downhole"
            ],
            root_causes=[
                "Incorrect BHCT estimation",
                "Over-retardation",
                "Contamination with mud thinners",
                "Low temperature (shallow/deepwater)"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Extend WOC time; verify BHCT; if confirmed, drill out and re-cement",
                    priority=1, duration_hours=24, success_probability=0.75,
                    estimated_cost_usd=80000,
                    resources_needed=["Cement unit", "Correct cement design"],
                    key_notes="Lab test cement with actual mud contamination"
                ),
            ],
            related_operations=["cementing"]
        ),
        OperationRisk(
            problem="Lost Circulation During Cementing",
            category="Cementing",
            severity=RiskLevel.HIGH,
            probability=0.12,
            npt_hours=18,
            early_warning_signs=[
                "Loss of returns during cement job",
                "Drop in surface pressure",
                "No cement returns at surface",
                "ECD exceeding fracture gradient"
            ],
            root_causes=[
                "Heavy cement slurry exceeding fracture gradient",
                "High pump rate creating excessive ECD",
                "Weak zone not isolated",
                "No lost circulation preventive additives"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Reduce pump rate; consider lightweight cement or foam cement",
                    priority=1, duration_hours=4, success_probability=0.65,
                    estimated_cost_usd=25000,
                    resources_needed=["Lightweight cement blend", "Nitrogen unit for foam"],
                    key_notes="Plan stage cementing if necessary"
                ),
                ContingencyStep(
                    action="Perform top-up cementing through annulus if cement not at surface",
                    priority=2, duration_hours=6, success_probability=0.80,
                    estimated_cost_usd=20000,
                    resources_needed=["Inner string / stinger", "Cement"],
                    key_notes="Common for surface casing cement jobs"
                ),
            ],
            related_operations=["cementing"]
        ),
        OperationRisk(
            problem="Stuck Casing Due to Premature Cement Setting",
            category="Cementing",
            severity=RiskLevel.CRITICAL,
            probability=0.03,
            npt_hours=72,
            early_warning_signs=[
                "Pump pressure increasing unexpectedly",
                "Cannot reciprocate casing",
                "Higher BHST than expected"
            ],
            root_causes=[
                "Incorrect thickening time design",
                "BHCT higher than predicted",
                "Cement mixed at wrong density",
                "Insufficient retarder"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Emergency: displace cement immediately if pumping still possible",
                    priority=1, duration_hours=2, success_probability=0.40,
                    estimated_cost_usd=50000,
                    resources_needed=["All available pumps", "Displacement fluid"],
                    key_notes="Time critical; every minute counts"
                ),
                ContingencyStep(
                    action="If casing cemented in place, drill out cement and re-evaluate",
                    priority=2, duration_hours=48, success_probability=0.60,
                    estimated_cost_usd=300000,
                    resources_needed=["Drill-out BHA", "Fishing tools if needed"],
                    key_notes="May require sidetrack; worst case"
                ),
            ],
            related_operations=["cementing"]
        ),
        OperationRisk(
            problem="Surface Equipment Failure During Cement Job",
            category="Equipment Failure",
            severity=RiskLevel.HIGH,
            probability=0.07,
            npt_hours=6,
            early_warning_signs=[
                "Pump pressure fluctuations",
                "Cement head leaking",
                "Manifold valves not operating"
            ],
            root_causes=[
                "Poor pre-job equipment testing",
                "Worn pump parts",
                "Cement head gasket failure",
                "Cold weather affecting equipment"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Switch to backup pump; repair inline; use rig pumps as backup",
                    priority=1, duration_hours=2, success_probability=0.80,
                    estimated_cost_usd=10000,
                    resources_needed=["Backup cement pump", "Rig pump manifold"],
                    key_notes="Always have backup pump tested and ready"
                ),
            ],
            related_operations=["cementing"]
        ),
        OperationRisk(
            problem="Gas Migration Through Cement",
            category="Cementing",
            severity=RiskLevel.HIGH,
            probability=0.10,
            npt_hours=24,
            early_warning_signs=[
                "Sustained annular pressure after cement",
                "Gas at surface in annulus",
                "CBL showing micro-annulus"
            ],
            root_causes=[
                "Gas percolation during cement transition",
                "Insufficient cement column height",
                "High gas pressure relative to cement",
                "Poor cement static gel strength development"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Apply annular pressure to hold gas; use gas-tight cement system",
                    priority=1, duration_hours=4, success_probability=0.70,
                    estimated_cost_usd=30000,
                    resources_needed=["Gas-tight cement (latex, right-angle-set)", "Pressure monitoring"],
                    key_notes="Prevention is key; use anti-gas migration additives"
                ),
                ContingencyStep(
                    action="Squeeze cement at gas migration zone if confirmed by logs",
                    priority=2, duration_hours=12, success_probability=0.65,
                    estimated_cost_usd=60000,
                    resources_needed=["Squeeze equipment", "Gas-tight cement"],
                    key_notes="May need to perforate and squeeze"
                ),
            ],
            related_operations=["cementing"]
        ),
        # =====================================================================
        # COMPLETION RISKS (38-46)
        # =====================================================================
        OperationRisk(
            problem="SSD (Sliding Sleeve Door) Stuck / Will Not Open",
            category="Completion",
            severity=RiskLevel.HIGH,
            probability=0.12,
            npt_hours=18,
            early_warning_signs=[
                "Slickline/coiled tubing unable to shift sleeve",
                "Excessive force required",
                "Multiple attempts needed"
            ],
            root_causes=[
                "Scale/debris buildup on sleeve",
                "Incorrect opening tool size",
                "Sleeve damaged during installation",
                "Differential pressure holding sleeve closed"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Re-attempt with correct size shifting tool; apply jarring force",
                    priority=1, duration_hours=4, success_probability=0.65,
                    estimated_cost_usd=15000,
                    resources_needed=["Correct shifting tool", "Slickline jars"],
                    key_notes="Verify OD of shifting tool matches sleeve profile"
                ),
                ContingencyStep(
                    action="Run coiled tubing with hydraulic shifting tool",
                    priority=2, duration_hours=12, success_probability=0.80,
                    estimated_cost_usd=50000,
                    resources_needed=["Coiled tubing unit", "Hydraulic shifter"],
                    key_notes="CT provides more force than slickline"
                ),
                ContingencyStep(
                    action="Millout sleeve and replace with new completion accessory",
                    priority=3, duration_hours=36, success_probability=0.75,
                    estimated_cost_usd=150000,
                    resources_needed=["Workover rig", "Mill", "Replacement sleeve"],
                    key_notes="Last resort; requires workover"
                ),
            ],
            related_operations=["completion", "slickline"]
        ),
        OperationRisk(
            problem="Packer Setting Failure",
            category="Completion",
            severity=RiskLevel.HIGH,
            probability=0.08,
            npt_hours=24,
            early_warning_signs=[
                "Unable to achieve setting pressure",
                "Packer slipping after set",
                "Pressure test failure"
            ],
            root_causes=[
                "Debris in casing preventing element seal",
                "Wrong casing ID for packer",
                "Insufficient setting force",
                "Element damage during running"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Re-attempt setting; ensure clean casing ID; check setting parameters",
                    priority=1, duration_hours=4, success_probability=0.60,
                    estimated_cost_usd=10000,
                    resources_needed=["Setting tool", "Pressure test equipment"],
                    key_notes="Run casing scraper/drift before packer"
                ),
                ContingencyStep(
                    action="POOH packer; inspect and replace; rerun",
                    priority=2, duration_hours=18, success_probability=0.85,
                    estimated_cost_usd=80000,
                    resources_needed=["Replacement packer", "Trip time"],
                    key_notes="Inspect casing with caliper if repeated failures"
                ),
            ],
            related_operations=["completion"]
        ),
        OperationRisk(
            problem="Tubing Leak (Completion String)",
            category="Completion Integrity",
            severity=RiskLevel.HIGH,
            probability=0.08,
            npt_hours=36,
            early_warning_signs=[
                "Pressure test failure on tubing",
                "Annular pressure buildup during production",
                "Fluid communication between tubing and annulus"
            ],
            root_causes=[
                "Connection make-up issues (under/over torque)",
                "Corrosion (CO2, H2S)",
                "Erosion from sand production",
                "Thread galling"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Identify leak depth with logging; pull and replace damaged tubing",
                    priority=1, duration_hours=36, success_probability=0.85,
                    estimated_cost_usd=200000,
                    resources_needed=["Workover rig", "Replacement tubing", "Logging tools"],
                    key_notes="Production logging or noise log to locate leak"
                ),
                ContingencyStep(
                    action="Install straddle packer across leak if workover not feasible",
                    priority=2, duration_hours=12, success_probability=0.65,
                    estimated_cost_usd=50000,
                    resources_needed=["Straddle packer"],
                    key_notes="Temporary solution; reduces ID"
                ),
            ],
            related_operations=["completion", "workover", "tubing"]
        ),
        OperationRisk(
            problem="Screen Plugging / Failure (Sand Control)",
            category="Completion",
            severity=RiskLevel.HIGH,
            probability=0.10,
            npt_hours=48,
            early_warning_signs=[
                "Increasing skin factor / reduced PI",
                "Sand production above limits",
                "Screen erosion indicators"
            ],
            root_causes=[
                "Incorrect screen size selection",
                "Improper gravel pack placement",
                "Fines migration plugging screens",
                "Screen collapse from high differential pressure"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Perform acid wash / solvent treatment through CT to clean screens",
                    priority=1, duration_hours=12, success_probability=0.55,
                    estimated_cost_usd=40000,
                    resources_needed=["Coiled tubing", "Acid/solvent treatment"],
                    key_notes="Monitor return fluids for sand"
                ),
                ContingencyStep(
                    action="Workover to replace screens; re-gravel pack",
                    priority=2, duration_hours=96, success_probability=0.80,
                    estimated_cost_usd=500000,
                    resources_needed=["Workover rig", "New screens", "Gravel"],
                    key_notes="Major intervention; high cost"
                ),
            ],
            related_operations=["completion"]
        ),
        OperationRisk(
            problem="Completion Equipment Stuck in Hole",
            category="Completion",
            severity=RiskLevel.HIGH,
            probability=0.06,
            npt_hours=36,
            early_warning_signs=[
                "Increasing drag running completion",
                "Cannot reach setting depth",
                "Cannot retrieve completion equipment"
            ],
            root_causes=[
                "Debris / fill in wellbore",
                "Casing restriction / deformation",
                "Scale buildup",
                "Differential sticking of packer element"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Work string; apply jars if available; circulate if possible",
                    priority=1, duration_hours=8, success_probability=0.50,
                    estimated_cost_usd=20000,
                    resources_needed=["Jars", "Circulation capability"],
                    key_notes="Avoid excessive force; risk of equipment damage"
                ),
                ContingencyStep(
                    action="Cut tubing above stuck point; fish separately",
                    priority=2, duration_hours=48, success_probability=0.70,
                    estimated_cost_usd=200000,
                    resources_needed=["Tubing cutter", "Fishing tools"],
                    key_notes="May lose lower completion"
                ),
            ],
            related_operations=["completion", "workover"]
        ),
        OperationRisk(
            problem="Subsurface Safety Valve (SSSV) Failure",
            category="Completion Integrity",
            severity=RiskLevel.CRITICAL,
            probability=0.07,
            npt_hours=24,
            early_warning_signs=[
                "SSSV fails to close on function test",
                "Control line pressure anomaly",
                "SSSV leaking on inflow test"
            ],
            root_causes=[
                "Scale/debris in valve mechanism",
                "Control line leak/damage",
                "Spring failure in fail-safe mechanism",
                "Corrosion of valve components"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Install wireline-set plug below SSSV as temporary barrier",
                    priority=1, duration_hours=6, success_probability=0.85,
                    estimated_cost_usd=25000,
                    resources_needed=["Wireline unit", "Bridge plug"],
                    key_notes="Regulatory requirement: must have two barriers"
                ),
                ContingencyStep(
                    action="Workover to replace SSSV",
                    priority=2, duration_hours=48, success_probability=0.90,
                    estimated_cost_usd=300000,
                    resources_needed=["Workover rig", "Replacement SSSV"],
                    key_notes="Plan for well kill and completion pull"
                ),
            ],
            related_operations=["completion", "workover"]
        ),
        OperationRisk(
            problem="Downhole Gauge / Monitoring Equipment Failure",
            category="Completion",
            severity=RiskLevel.LOW,
            probability=0.15,
            npt_hours=0,
            early_warning_signs=[
                "Loss of signal from downhole gauges",
                "Erratic readings",
                "Communication failure"
            ],
            root_causes=[
                "Electronic component failure",
                "Cable/connector damage during installation",
                "Temperature/pressure exceeding ratings",
                "Chemical attack"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Switch to redundant gauge if installed; plan workover for replacement",
                    priority=1, duration_hours=0, success_probability=0.50,
                    estimated_cost_usd=0,
                    resources_needed=["Redundant gauge system"],
                    key_notes="Always install redundant gauges"
                ),
                ContingencyStep(
                    action="Use periodic wireline pressure surveys as alternative",
                    priority=2, duration_hours=6, success_probability=0.90,
                    estimated_cost_usd=15000,
                    resources_needed=["Wireline unit", "Pressure gauges"],
                    key_notes="Higher operational cost over time"
                ),
            ],
            related_operations=["completion"]
        ),
        OperationRisk(
            problem="Inflow Control Device (ICD) Plugging or Failure",
            category="Completion",
            severity=RiskLevel.MEDIUM,
            probability=0.10,
            npt_hours=24,
            early_warning_signs=[
                "Uneven inflow profile on PLT",
                "Higher skin than expected",
                "Water/gas breakthrough patterns"
            ],
            root_causes=[
                "Fines/debris plugging ICD nozzles",
                "Incorrect ICD sizing",
                "Completion fluid damage"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="CT acid stimulation targeted at plugged ICDs",
                    priority=1, duration_hours=12, success_probability=0.55,
                    estimated_cost_usd=60000,
                    resources_needed=["Coiled tubing", "Acid treatment"],
                    key_notes="Limited effectiveness once nozzles are blocked"
                ),
            ],
            related_operations=["completion"]
        ),
        OperationRisk(
            problem="Gravel Pack Failure",
            category="Sand Control",
            severity=RiskLevel.HIGH,
            probability=0.08,
            npt_hours=48,
            early_warning_signs=[
                "Sand production at surface",
                "Erosion in surface equipment",
                "Decrease in production rate"
            ],
            root_causes=[
                "Void spaces in gravel pack",
                "Screen failure allowing gravel migration",
                "Incorrect gravel size selection",
                "Shunt tube failure during placement"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Perform gravel pack top-up if voids accessible",
                    priority=1, duration_hours=24, success_probability=0.60,
                    estimated_cost_usd=100000,
                    resources_needed=["Gravel pack equipment", "Gravel"],
                    key_notes="May need through-tubing approach"
                ),
                ContingencyStep(
                    action="Install chemical consolidation treatment",
                    priority=2, duration_hours=12, success_probability=0.50,
                    estimated_cost_usd=50000,
                    resources_needed=["Resin chemicals", "CT unit"],
                    key_notes="Temporary solution; may reduce permeability"
                ),
            ],
            related_operations=["completion"]
        ),
        # =====================================================================
        # PERFORATION RISKS (47-50)
        # =====================================================================
        OperationRisk(
            problem="Gun Misfire / Perforation Failure",
            category="Perforation",
            severity=RiskLevel.HIGH,
            probability=0.08,
            npt_hours=12,
            early_warning_signs=[
                "No pressure indication of detonation",
                "CCL depth correlation issues",
                "Surface system malfunction"
            ],
            root_causes=[
                "Detonator failure",
                "Wiring / connector issues",
                "Depth correlation error",
                "Safety system preventing fire",
                "Extreme well conditions (temperature)"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Retrieve guns safely; inspect and re-arm; re-run",
                    priority=1, duration_hours=8, success_probability=0.80,
                    estimated_cost_usd=30000,
                    resources_needed=["Wireline unit", "Backup gun system", "EOD procedures"],
                    key_notes="Follow explosive safety procedures for misfire"
                ),
                ContingencyStep(
                    action="Switch to TCP (tubing-conveyed perforation) if wireline guns fail",
                    priority=2, duration_hours=18, success_probability=0.90,
                    estimated_cost_usd=80000,
                    resources_needed=["TCP gun assembly", "Tubing", "Firing head"],
                    key_notes="TCP provides more reliable detonation in deviated wells"
                ),
            ],
            related_operations=["perforation"]
        ),
        OperationRisk(
            problem="Perforation in Wrong Interval",
            category="Perforation",
            severity=RiskLevel.CRITICAL,
            probability=0.03,
            npt_hours=36,
            early_warning_signs=[
                "Unexpected fluid production (water/gas)",
                "Depth correlation concerns pre-shot",
                "CCL not matching expected pattern"
            ],
            root_causes=[
                "Depth correlation error",
                "Incorrect log depth reference",
                "Pipe stretch/compression calculation error",
                "Human error in depth tracking"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Squeeze-off wrong perforations with cement",
                    priority=1, duration_hours=12, success_probability=0.75,
                    estimated_cost_usd=50000,
                    resources_needed=["Squeeze packer", "Cement"],
                    key_notes="Verify correct interval before re-perforating"
                ),
                ContingencyStep(
                    action="Re-perforate correct interval after squeeze confirmation",
                    priority=2, duration_hours=8, success_probability=0.90,
                    estimated_cost_usd=40000,
                    resources_needed=["Perforation guns", "Depth correlation tools"],
                    key_notes="Double-check depth correlation with multiple references"
                ),
            ],
            related_operations=["perforation"]
        ),
        OperationRisk(
            problem="Perforation Gun Stuck in Hole",
            category="Perforation",
            severity=RiskLevel.HIGH,
            probability=0.06,
            npt_hours=24,
            early_warning_signs=[
                "Gun assembly cannot be pulled up",
                "Obstruction during pull out",
                "Cable tension anomalies"
            ],
            root_causes=[
                "Debris/fill below guns",
                "Gun OD too large for casing ID / restrictions",
                "Swelling of fired charges",
                "Casing deformation"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Work gun assembly with jarring; try to rotate if using tubing-conveyed",
                    priority=1, duration_hours=8, success_probability=0.60,
                    estimated_cost_usd=20000,
                    resources_needed=["Jars", "Fishing engineer"],
                    key_notes="If wireline, risk of cable parting"
                ),
                ContingencyStep(
                    action="Cut cable/tubing; mill over guns; fish out debris",
                    priority=2, duration_hours=36, success_probability=0.70,
                    estimated_cost_usd=150000,
                    resources_needed=["Tubing cutter", "Milling tools", "Fishing tools"],
                    key_notes="Handle unfired charges with extreme caution"
                ),
            ],
            related_operations=["perforation", "fishing"]
        ),
        OperationRisk(
            problem="Well Kicks After Perforation (Underbalanced Perforation Issues)",
            category="Well Control",
            severity=RiskLevel.HIGH,
            probability=0.10,
            npt_hours=8,
            early_warning_signs=[
                "Immediate flow after perforation",
                "Surface pressure buildup",
                "Insufficient kill weight fluid in hole"
            ],
            root_causes=[
                "Higher pore pressure than expected",
                "Insufficient completion fluid density",
                "Large perforation interval with high productivity"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Close well using Xmas tree/BOP; circulate kill weight fluid",
                    priority=1, duration_hours=4, success_probability=0.90,
                    estimated_cost_usd=15000,
                    resources_needed=["Kill fluid", "Well control equipment"],
                    key_notes="Controlled flow may be desired for clean-up"
                ),
            ],
            related_operations=["perforation", "well_testing"]
        ),
        # =====================================================================
        # WELL TESTING RISKS (51-55)
        # =====================================================================
        OperationRisk(
            problem="Surface Well Test Equipment Leak",
            category="Well Testing",
            severity=RiskLevel.HIGH,
            probability=0.10,
            npt_hours=8,
            early_warning_signs=[
                "Visible leak at connections",
                "Pressure test failure",
                "HSE alarms from gas detectors"
            ],
            root_causes=[
                "Gasket / seal failure",
                "Connection make-up issues",
                "Erosion from sand",
                "Corrosion from H2S/CO2"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Shut in well; isolate and repair leak; pressure test before resuming",
                    priority=1, duration_hours=4, success_probability=0.90,
                    estimated_cost_usd=10000,
                    resources_needed=["Spare gaskets/seals", "Test equipment crew"],
                    key_notes="Do not tighten connections under pressure"
                ),
            ],
            related_operations=["well_testing"]
        ),
        OperationRisk(
            problem="Hydrate Formation During Well Test / Flowback",
            category="Flow Assurance",
            severity=RiskLevel.HIGH,
            probability=0.10,
            npt_hours=12,
            early_warning_signs=[
                "Pressure drop across choke increasing",
                "Erratic flow rate",
                "Ice formation on surface equipment",
                "Blocked flow line"
            ],
            root_causes=[
                "Low temperature + high pressure (hydrate envelope)",
                "Water production with gas",
                "Joule-Thomson cooling across choke",
                "No hydrate inhibitor in system"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Inject methanol/MEG upstream of choke; apply heat if accessible",
                    priority=1, duration_hours=4, success_probability=0.80,
                    estimated_cost_usd=15000,
                    resources_needed=["Methanol/MEG injection pump", "Chemical supply"],
                    key_notes="Prevention: continuous injection during flow"
                ),
                ContingencyStep(
                    action="Depressurize from both sides to dissociate hydrate plug",
                    priority=2, duration_hours=8, success_probability=0.70,
                    estimated_cost_usd=5000,
                    resources_needed=["Depressurization capability"],
                    key_notes="Never apply pressure behind hydrate plug (projectile risk)"
                ),
            ],
            related_operations=["well_testing", "completion"]
        ),
        OperationRisk(
            problem="Downhole Test Tool (DST) Failure",
            category="Well Testing",
            severity=RiskLevel.HIGH,
            probability=0.08,
            npt_hours=24,
            early_warning_signs=[
                "Tool not responding to commands",
                "Unexpected pressure behavior",
                "Cannot open/close downhole tester valve"
            ],
            root_causes=[
                "Mechanical failure of test tool",
                "Debris blocking tool operation",
                "Pressure / temperature exceeding tool rating",
                "Annulus pressure control issues"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Attempt backup activation method (ball drop, annulus pressure)",
                    priority=1, duration_hours=4, success_probability=0.60,
                    estimated_cost_usd=5000,
                    resources_needed=["Ball/bar activation", "Annulus pressure"],
                    key_notes="Know all activation methods before RIH"
                ),
                ContingencyStep(
                    action="POOH test string; inspect and replace tool; re-run test",
                    priority=2, duration_hours=24, success_probability=0.85,
                    estimated_cost_usd=100000,
                    resources_needed=["Replacement test tool", "Trip time"],
                    key_notes="Full function test on surface before re-running"
                ),
            ],
            related_operations=["well_testing"]
        ),
        OperationRisk(
            problem="Sand Production During Well Test",
            category="Well Testing",
            severity=RiskLevel.MEDIUM,
            probability=0.15,
            npt_hours=8,
            early_warning_signs=[
                "Sand detector activating",
                "Erosion in choke/flow line",
                "Fluctuating flow rates",
                "Acoustic sand monitors alarming"
            ],
            root_causes=[
                "Unconsolidated formation",
                "Excessive drawdown",
                "No sand control completion",
                "Formation failure from depletion"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Reduce choke size to lower drawdown; monitor sand rate",
                    priority=1, duration_hours=1, success_probability=0.75,
                    estimated_cost_usd=0,
                    resources_needed=["Sand monitoring equipment", "Choke control"],
                    key_notes="Determine critical drawdown for sand production"
                ),
                ContingencyStep(
                    action="Shut in well if sand production exceeds equipment limits",
                    priority=2, duration_hours=2, success_probability=0.95,
                    estimated_cost_usd=5000,
                    resources_needed=["Well shut-in capability"],
                    key_notes="Sand can erode surface equipment rapidly"
                ),
            ],
            related_operations=["well_testing"]
        ),
        OperationRisk(
            problem="Well Clean-up Failure / Formation Damage During Test",
            category="Well Testing",
            severity=RiskLevel.MEDIUM,
            probability=0.12,
            npt_hours=12,
            early_warning_signs=[
                "Flow rate much lower than expected",
                "Heavy mud/completion fluid still returning",
                "High skin factor from pressure analysis"
            ],
            root_causes=[
                "Drilling fluid invasion / filter cake damage",
                "Completion fluid losses to formation",
                "Perforation damage (crushed zone)",
                "Fines mobilization blocking perfs"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Extend clean-up flow period; gradually increase choke size",
                    priority=1, duration_hours=12, success_probability=0.60,
                    estimated_cost_usd=20000,
                    resources_needed=["Extended test time", "Burner/flare capacity"],
                    key_notes="Some wells need 24+ hours of clean-up"
                ),
                ContingencyStep(
                    action="Pump acid stimulation treatment to remove damage",
                    priority=2, duration_hours=8, success_probability=0.70,
                    estimated_cost_usd=50000,
                    resources_needed=["CT or bullhead", "Acid/solvent treatment"],
                    key_notes="Design acid based on formation mineralogy"
                ),
            ],
            related_operations=["well_testing"]
        ),
        # =====================================================================
        # FISHING RISKS (56-58)
        # =====================================================================
        OperationRisk(
            problem="Fishing Tool Engagement Failure",
            category="Fishing",
            severity=RiskLevel.HIGH,
            probability=0.15,
            npt_hours=12,
            early_warning_signs=[
                "Overshot not catching fish",
                "Cannot tag fish top properly",
                "Multiple attempts without engagement"
            ],
            root_causes=[
                "Incorrect fish dimensions",
                "Fish top damaged / burred",
                "Wrong overshot/grapple size",
                "Debris covering fish top"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Run impression block to verify fish top condition and dimensions",
                    priority=1, duration_hours=6, success_probability=0.85,
                    estimated_cost_usd=10000,
                    resources_needed=["Impression block", "Lead paint"],
                    key_notes="Always run impression block before fishing"
                ),
                ContingencyStep(
                    action="Try alternative fishing tool (spear, reverse circulation junk basket)",
                    priority=2, duration_hours=12, success_probability=0.65,
                    estimated_cost_usd=25000,
                    resources_needed=["Alternative fishing tools", "Fishing engineer"],
                    key_notes="Adapt approach based on impression block results"
                ),
            ],
            related_operations=["fishing"]
        ),
        OperationRisk(
            problem="Secondary Fish (Fishing Tool Stuck/Failed)",
            category="Fishing",
            severity=RiskLevel.CRITICAL,
            probability=0.08,
            npt_hours=48,
            early_warning_signs=[
                "Cannot release from first fish",
                "Fishing tool stuck",
                "Overpull approaching limits"
            ],
            root_causes=[
                "Pack-off around fishing assembly",
                "Grapple cannot release from fish",
                "Differential sticking of fishing BHA"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Back off fishing string above fish; plan second fishing operation",
                    priority=1, duration_hours=12, success_probability=0.60,
                    estimated_cost_usd=50000,
                    resources_needed=["Free point indicator", "Back-off tools", "String shot"],
                    key_notes="Determine free point before back-off"
                ),
                ContingencyStep(
                    action="Sidetrack around combined fish if fishing becomes uneconomical",
                    priority=2, duration_hours=96, success_probability=0.85,
                    estimated_cost_usd=500000,
                    resources_needed=["Cement", "Sidetrack BHA", "Casing"],
                    key_notes="Cost-benefit analysis: fishing vs sidetrack"
                ),
            ],
            related_operations=["fishing"]
        ),
        OperationRisk(
            problem="Wireline/Slickline Fish in Hole",
            category="Fishing",
            severity=RiskLevel.MEDIUM,
            probability=0.08,
            npt_hours=12,
            early_warning_signs=[
                "Wire broke or parted downhole",
                "Tool stuck and cable parted on overpull",
                "Lost tools in completion"
            ],
            root_causes=[
                "Wire fatigue / corrosion",
                "Excessive tension",
                "Tool hang-up in completion",
                "Wire line cut on sharp edge"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Fish with wireline overshot / grab tool",
                    priority=1, duration_hours=6, success_probability=0.70,
                    estimated_cost_usd=15000,
                    resources_needed=["Fishing grab tools", "Wireline unit"],
                    key_notes="Identify fish dimensions from tool tally"
                ),
                ContingencyStep(
                    action="Fish with coiled tubing if wireline fishing unsuccessful",
                    priority=2, duration_hours=12, success_probability=0.80,
                    estimated_cost_usd=40000,
                    resources_needed=["CT unit", "CT fishing tools"],
                    key_notes="CT provides better control in deviated wells"
                ),
            ],
            related_operations=["fishing", "slickline", "completion"]
        ),
        # =====================================================================
        # WORKOVER RISKS (59-63)
        # =====================================================================
        OperationRisk(
            problem="Well Control During Workover (Live Well Intervention)",
            category="Well Control",
            severity=RiskLevel.CRITICAL,
            probability=0.08,
            npt_hours=24,
            early_warning_signs=[
                "Unexpected flow from well during workover",
                "Kill fluid density insufficient",
                "Barrier failure during intervention"
            ],
            root_causes=[
                "Insufficient kill weight fluid",
                "Unknown pressure from depleted/charged zones",
                "Barrier failure (plug, packer)",
                "Communication behind casing"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Shut in well; verify barriers; prepare kill operation",
                    priority=1, duration_hours=4, success_probability=0.90,
                    estimated_cost_usd=20000,
                    resources_needed=["BOP", "Kill fluid", "Well control crew"],
                    key_notes="Always have two barriers in place during workover"
                ),
                ContingencyStep(
                    action="Bullhead kill fluid to control formation",
                    priority=2, duration_hours=6, success_probability=0.80,
                    estimated_cost_usd=30000,
                    resources_needed=["Kill fluid", "High pressure pumps"],
                    key_notes="Monitor surface pressures carefully"
                ),
            ],
            related_operations=["workover"]
        ),
        OperationRisk(
            problem="Casing / Tubing Corrosion Found During Workover",
            category="Integrity",
            severity=RiskLevel.HIGH,
            probability=0.12,
            npt_hours=36,
            early_warning_signs=[
                "Caliper log showing wall loss",
                "Pitting observed on pulled tubing",
                "Annular fluid samples showing corrosion products"
            ],
            root_causes=[
                "CO2 / H2S corrosion",
                "Galvanic corrosion between dissimilar metals",
                "Microbiologically influenced corrosion (MIC)",
                "Insufficient corrosion inhibitor treatment"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Run casing inspection log (MFL/UT); assess remaining wall thickness",
                    priority=1, duration_hours=8, success_probability=0.90,
                    estimated_cost_usd=30000,
                    resources_needed=["Casing inspection tool (MFL/UT)", "Logging crew"],
                    key_notes="Compare with minimum wall for burst/collapse"
                ),
                ContingencyStep(
                    action="Install casing patch or liner over corroded section",
                    priority=2, duration_hours=48, success_probability=0.80,
                    estimated_cost_usd=250000,
                    resources_needed=["Casing patch/liner", "Cement if needed"],
                    key_notes="Plan for reduced ID"
                ),
            ],
            related_operations=["workover"]
        ),
        OperationRisk(
            problem="Scale Buildup in Tubing/Completion",
            category="Production Chemistry",
            severity=RiskLevel.MEDIUM,
            probability=0.15,
            npt_hours=12,
            early_warning_signs=[
                "Declining production rate",
                "Increasing wellhead pressure for same rate",
                "Scale samples at surface",
                "Restriction felt during wireline runs"
            ],
            root_causes=[
                "Incompatible water mixing (barium sulfate)",
                "Calcium carbonate from pressure/temperature changes",
                "Lack of scale inhibitor squeeze treatment",
                "Water breakthrough"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Coiled tubing scale removal (mechanical + chemical)",
                    priority=1, duration_hours=12, success_probability=0.75,
                    estimated_cost_usd=50000,
                    resources_needed=["CT unit", "Scale dissolver", "Milling tools"],
                    key_notes="Use appropriate dissolver for scale type"
                ),
                ContingencyStep(
                    action="Plan scale inhibitor squeeze treatment program",
                    priority=2, duration_hours=6, success_probability=0.80,
                    estimated_cost_usd=20000,
                    resources_needed=["Scale inhibitor chemicals", "Pumping equipment"],
                    key_notes="Prevention: regular squeeze treatments"
                ),
            ],
            related_operations=["workover", "completion"]
        ),
        OperationRisk(
            problem="Artificial Lift Equipment Failure",
            category="Workover",
            severity=RiskLevel.MEDIUM,
            probability=0.15,
            npt_hours=24,
            early_warning_signs=[
                "Declining production rate",
                "ESP motor overheating / high amp draw",
                "Rod pump irregular dynamometer cards",
                "Gas lift valve failure"
            ],
            root_causes=[
                "ESP motor/pump failure",
                "Rod string fatigue/parting",
                "Gas lift valve erosion",
                "Power/cable failure",
                "Sand erosion of lift equipment"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Diagnose failure type; plan equipment replacement workover",
                    priority=1, duration_hours=8, success_probability=0.90,
                    estimated_cost_usd=150000,
                    resources_needed=["Workover rig", "Replacement equipment"],
                    key_notes="Have backup equipment pre-ordered"
                ),
            ],
            related_operations=["workover", "completion"]
        ),
        OperationRisk(
            problem="Window Milling / Sidetrack Failure",
            category="Workover",
            severity=RiskLevel.HIGH,
            probability=0.10,
            npt_hours=36,
            early_warning_signs=[
                "Slow milling progress",
                "Whipstock shifted / moved",
                "BHA deviation from plan",
                "Mill wear indicators"
            ],
            root_causes=[
                "Hard casing grade difficult to mill",
                "Whipstock orientation issues",
                "Mill wear/failure",
                "Pack off of casing swarf"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Trip for fresh mill; verify whipstock orientation; optimize parameters",
                    priority=1, duration_hours=12, success_probability=0.75,
                    estimated_cost_usd=40000,
                    resources_needed=["Fresh mills", "Directional tools"],
                    key_notes="Use junk magnet to clean swarf; proper flow rate"
                ),
                ContingencyStep(
                    action="Pull whipstock; reorient and reset at correct depth/azimuth",
                    priority=2, duration_hours=24, success_probability=0.80,
                    estimated_cost_usd=80000,
                    resources_needed=["Whipstock", "Orientation tools"],
                    key_notes="Verify with gyro survey"
                ),
            ],
            related_operations=["workover", "fishing"]
        ),
        # =====================================================================
        # TUBING RISKS (64-66)
        # =====================================================================
        OperationRisk(
            problem="Tubing Parting / Failure Downhole",
            category="Tubing Integrity",
            severity=RiskLevel.HIGH,
            probability=0.06,
            npt_hours=48,
            early_warning_signs=[
                "Sudden change in surface pressure",
                "Communication between tubing and annulus",
                "Anomalous noise log results"
            ],
            root_causes=[
                "Corrosion fatigue",
                "Tension from thermal cycling",
                "Connection failure (incorrect torque)",
                "Erosion from sand"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Kill well; POOH tubing above failure; fish lower section",
                    priority=1, duration_hours=36, success_probability=0.75,
                    estimated_cost_usd=200000,
                    resources_needed=["Workover rig", "Fishing tools"],
                    key_notes="Locate failure depth with tubing tally and caliper"
                ),
            ],
            related_operations=["tubing", "workover"]
        ),
        OperationRisk(
            problem="Tubing Collapse Due to Annular Pressure",
            category="Tubing Integrity",
            severity=RiskLevel.HIGH,
            probability=0.04,
            npt_hours=36,
            early_warning_signs=[
                "Annular pressure buildup",
                "Restriction to wireline / CT passage",
                "Production rate decline without explanation"
            ],
            root_causes=[
                "Trapped annular fluid thermal expansion",
                "Fluid migration behind casing",
                "Tubing grade insufficient for annular loads",
                "No APB mitigation in design"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Bleed annular pressure; install rupture disk if recurring",
                    priority=1, duration_hours=2, success_probability=0.80,
                    estimated_cost_usd=5000,
                    resources_needed=["Pressure bleed capability"],
                    key_notes="Design for annular pressure buildup in initial well design"
                ),
                ContingencyStep(
                    action="Workover to replace collapsed tubing section",
                    priority=2, duration_hours=48, success_probability=0.85,
                    estimated_cost_usd=300000,
                    resources_needed=["Workover rig", "Replacement tubing"],
                    key_notes="Upgrade tubing grade if design deficiency"
                ),
            ],
            related_operations=["tubing", "completion"]
        ),
        OperationRisk(
            problem="Tubing Stuck in Packer (Cannot Release)",
            category="Workover",
            severity=RiskLevel.HIGH,
            probability=0.08,
            npt_hours=24,
            early_warning_signs=[
                "Cannot unset packer with normal procedure",
                "Excessive pickup weight without release",
                "Tubing stretch without packer release"
            ],
            root_causes=[
                "Scale/debris around packer bore",
                "Packer mechanism failure",
                "Excessive differential pressure across packer",
                "Corrosion bonding tubing to packer"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Apply chemical soak at packer; work string with jars",
                    priority=1, duration_hours=8, success_probability=0.50,
                    estimated_cost_usd=15000,
                    resources_needed=["Chemical wash", "Jars"],
                    key_notes="Soak minimum 4 hours"
                ),
                ContingencyStep(
                    action="Cut tubing above packer; mill packer out",
                    priority=2, duration_hours=24, success_probability=0.75,
                    estimated_cost_usd=100000,
                    resources_needed=["Tubing cutter", "Packer milling tools"],
                    key_notes="Verify what's below packer before milling"
                ),
            ],
            related_operations=["workover", "tubing"]
        ),
        # =====================================================================
        # SLICKLINE / WIRELINE RISKS (67-68)
        # =====================================================================
        OperationRisk(
            problem="Slickline Wire Parting",
            category="Slickline Operations",
            severity=RiskLevel.MEDIUM,
            probability=0.10,
            npt_hours=8,
            early_warning_signs=[
                "Wire fatigue indicators (curl test failure)",
                "High tension during operation",
                "Corrosion on wire"
            ],
            root_causes=[
                "Wire fatigue from repeated runs",
                "Exceeding safe working load",
                "Sharp edges in wellhead/tree",
                "Corrosion damage"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Fish with slickline grab tool / overshot",
                    priority=1, duration_hours=6, success_probability=0.75,
                    estimated_cost_usd=15000,
                    resources_needed=["Slickline fishing tools", "Spare wire"],
                    key_notes="Know last tool depth; run gauge ring first"
                ),
            ],
            related_operations=["slickline", "completion"]
        ),
        OperationRisk(
            problem="Logging Tool Stuck in Well (Open Hole)",
            category="Logging",
            severity=RiskLevel.HIGH,
            probability=0.08,
            npt_hours=24,
            early_warning_signs=[
                "Increasing cable tension",
                "Tool hung up at known tight spots",
                "Borehole collapse while logging"
            ],
            root_causes=[
                "Borehole instability / collapse behind tool",
                "Key seating of cable",
                "Differential sticking of pad tools",
                "Swelling shale"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Work cable up/down; pump mud to free tool; use wireline jars",
                    priority=1, duration_hours=8, success_probability=0.60,
                    estimated_cost_usd=20000,
                    resources_needed=["Wireline jars", "Rig pumps"],
                    key_notes="Do not exceed safe cable tension"
                ),
                ContingencyStep(
                    action="Cut cable; fish logging tool with drill pipe conveyed tools",
                    priority=2, duration_hours=24, success_probability=0.65,
                    estimated_cost_usd=80000,
                    resources_needed=["Overshot", "Drill pipe", "Fishing engineer"],
                    key_notes="Radioactive sources require special recovery procedures"
                ),
            ],
            related_operations=["logging", "fishing"]
        ),
        # =====================================================================
        # ADDITIONAL OPERATIONAL RISKS (69-72)
        # =====================================================================
        OperationRisk(
            problem="BOP Failure / Malfunction",
            category="Well Control Equipment",
            severity=RiskLevel.CRITICAL,
            probability=0.04,
            npt_hours=36,
            early_warning_signs=[
                "BOP test failure",
                "Slow ram closure",
                "Hydraulic system anomalies",
                "Annular preventer leak"
            ],
            root_causes=[
                "Hydraulic system failure",
                "Ram / element wear",
                "Control system malfunction",
                "Seal deterioration"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Activate secondary / backup control system; use accumulator backup",
                    priority=1, duration_hours=1, success_probability=0.85,
                    estimated_cost_usd=5000,
                    resources_needed=["Backup control system", "Accumulator"],
                    key_notes="Must have minimum 2 methods to close each ram"
                ),
                ContingencyStep(
                    action="Shut down operations; repair/replace BOP; retest per API RP 53",
                    priority=2, duration_hours=24, success_probability=0.95,
                    estimated_cost_usd=100000,
                    resources_needed=["BOP spare parts", "BOP technician"],
                    key_notes="Cannot drill ahead until BOP fully functional and tested"
                ),
            ],
            related_operations=["drilling", "workover", "tripping"]
        ),
        OperationRisk(
            problem="Rig Equipment Failure (Top Drive / Drawworks / Pumps)",
            category="Rig Equipment",
            severity=RiskLevel.MEDIUM,
            probability=0.10,
            npt_hours=12,
            early_warning_signs=[
                "Unusual noise / vibration from equipment",
                "Performance degradation",
                "Warning alarms on control systems",
                "Fluid leaks from hydraulic systems"
            ],
            root_causes=[
                "Mechanical wear and fatigue",
                "Insufficient preventive maintenance",
                "Electrical system failure",
                "Overloading"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Switch to backup system if available; initiate repair",
                    priority=1, duration_hours=8, success_probability=0.80,
                    estimated_cost_usd=30000,
                    resources_needed=["Spare parts", "Rig mechanic/electrician"],
                    key_notes="Ensure critical spares on rig"
                ),
            ],
            related_operations=["drilling", "tripping", "casing_running"]
        ),
        OperationRisk(
            problem="Weather Downtime (Offshore)",
            category="External",
            severity=RiskLevel.MEDIUM,
            probability=0.15,
            npt_hours=24,
            early_warning_signs=[
                "Weather forecast deterioration",
                "Increasing wave height / wind speed",
                "Vessel motion increasing"
            ],
            root_causes=[
                "Storm / cyclone / hurricane",
                "Monsoon season operations",
                "Fog affecting helicopter operations"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Secure well with adequate barriers; prepare for rig move-off if required",
                    priority=1, duration_hours=12, success_probability=0.95,
                    estimated_cost_usd=100000,
                    resources_needed=["Weather monitoring", "Rig positioning system"],
                    key_notes="Follow rig-specific weather criteria and evacuation plan"
                ),
            ],
            related_operations=["drilling", "completion", "well_testing"]
        ),
        OperationRisk(
            problem="Environmental Spill / HSE Incident",
            category="HSE",
            severity=RiskLevel.CRITICAL,
            probability=0.03,
            npt_hours=48,
            early_warning_signs=[
                "Fluid observed outside containment",
                "Abnormal discharge in cuttings",
                "SBM/OBM discharge detected"
            ],
            root_causes=[
                "Equipment failure (tank, line, seal)",
                "Operator error",
                "Well control event",
                "Inadequate containment"
            ],
            contingency_plans=[
                ContingencyStep(
                    action="Activate OSRP (Oil Spill Response Plan); contain spill; report to authorities",
                    priority=1, duration_hours=4, success_probability=0.80,
                    estimated_cost_usd=200000,
                    resources_needed=["Spill response equipment", "Booms", "Skimmers"],
                    key_notes="Regulatory reporting within required timeframe"
                ),
            ],
            related_operations=["drilling", "well_testing", "workover"]
        ),
    ]
    return risks


def build_forgotten_items() -> List[ForgottenItem]:
    """Build the list of commonly forgotten best-practice items."""
    items = [
        ForgottenItem(
            description="BOP Function & Pressure Test Before Drilling Out",
            related_operations=["drilling", "casing_running", "workover"],
            severity=RiskLevel.CRITICAL,
            recommended_action="Test BOP per API RP 53 schedule; function test all rams and annular before each section",
            reference="API RP 53, IADC Well Control Guidelines"
        ),
        ForgottenItem(
            description="Trip Tank Calibration and Continuous Monitoring",
            related_operations=["tripping", "drilling"],
            severity=RiskLevel.HIGH,
            recommended_action="Calibrate trip tank before each trip; assign dedicated person to monitor and record volumes",
            reference="IADC Well Control Manual"
        ),
        ForgottenItem(
            description="Kill Weight Mud Ready Before Drilling Into New Zone",
            related_operations=["drilling"],
            severity=RiskLevel.CRITICAL,
            recommended_action="Prepare and stage sufficient kill weight mud volume before drilling into predicted overpressure zone",
            reference="API RP 59, Well Control Manual"
        ),
        ForgottenItem(
            description="Casing Centralizer Placement per Design",
            related_operations=["casing_running", "cementing"],
            severity=RiskLevel.HIGH,
            recommended_action="Verify centralizer placement matches cement program design; use standoff analysis results",
            reference="API RP 10D-2, Cementing Best Practices"
        ),
        ForgottenItem(
            description="Shoe Track Cement Integrity Verification",
            related_operations=["cementing", "drilling"],
            severity=RiskLevel.HIGH,
            recommended_action="Perform positive and negative pressure test on shoe after cement WOC before drilling ahead",
            reference="API RP 65-2"
        ),
        ForgottenItem(
            description="Formation Integrity Test (FIT/LOT) After Drilling Out Shoe",
            related_operations=["drilling", "cementing"],
            severity=RiskLevel.HIGH,
            recommended_action="Perform LOT/FIT to verify shoe strength and mud weight window for next section",
            reference="Industry Standard Practice"
        ),
        ForgottenItem(
            description="Drill Pipe Inspection (TH Hill Category)",
            related_operations=["drilling", "tripping"],
            severity=RiskLevel.MEDIUM,
            recommended_action="Ensure drill pipe inspection is current (DS-1 Category 3 minimum); inspect on each trip",
            reference="DS-1 Volume 3, API RP 7G"
        ),
        ForgottenItem(
            description="Slow Pump Rate Pressure (SPR) Check",
            related_operations=["drilling"],
            severity=RiskLevel.HIGH,
            recommended_action="Record slow pump rate pressures at beginning of each tour and after any BHA change",
            reference="Well Control SOPs"
        ),
        ForgottenItem(
            description="Mud Properties Check Before POOH for Casing",
            related_operations=["tripping", "casing_running"],
            severity=RiskLevel.HIGH,
            recommended_action="Condition mud to correct weight and properties; circulate bottoms-up before POOH",
            reference="Mud Engineering Best Practices"
        ),
        ForgottenItem(
            description="Wiper Trip Before Running Casing",
            related_operations=["tripping", "casing_running"],
            severity=RiskLevel.HIGH,
            recommended_action="Perform short wiper trip to verify hole condition before committing casing to hole",
            reference="Casing Running Best Practices"
        ),
        ForgottenItem(
            description="Drift / Gauge Ring Run Before Running Completion",
            related_operations=["completion", "workover"],
            severity=RiskLevel.MEDIUM,
            recommended_action="Run drift/gauge ring on wireline/pipe to verify casing ID is clear and gauged",
            reference="Completion Running Procedures"
        ),
        ForgottenItem(
            description="Casing Scraper Run Before Completion",
            related_operations=["completion", "workover"],
            severity=RiskLevel.MEDIUM,
            recommended_action="Run casing scraper to clean debris/cement from inside casing before running completion",
            reference="Completion Best Practices"
        ),
        ForgottenItem(
            description="Tubing Pressure Test After Make-Up",
            related_operations=["completion", "tubing"],
            severity=RiskLevel.HIGH,
            recommended_action="Pressure test tubing string (internal and external) before setting packer",
            reference="Completion Integrity Standards"
        ),
        ForgottenItem(
            description="Emergency Disconnect Package (EDP) Function Test",
            related_operations=["drilling"],
            severity=RiskLevel.CRITICAL,
            recommended_action="Function test EDP system and verify rig quick-disconnect capability (offshore/subsea)",
            reference="API RP 53, Deepwater Well Control"
        ),
        ForgottenItem(
            description="Pre-Job Safety Meeting (Toolbox Talk) for Critical Operations",
            related_operations=["drilling", "tripping", "casing_running", "cementing", "completion",
                               "perforation", "well_testing", "fishing", "workover", "slickline", "logging"],
            severity=RiskLevel.HIGH,
            recommended_action="Conduct documented pre-job safety meeting with all crew before each critical operation",
            reference="IADC HSE Guidelines, Company SIMOPS Procedures"
        ),
        ForgottenItem(
            description="Cement Bond Log (CBL) Run After Primary Cementing",
            related_operations=["cementing"],
            severity=RiskLevel.MEDIUM,
            recommended_action="Schedule CBL/VDL log to evaluate cement bond quality; compare with offset well data",
            reference="API RP 10B-2"
        ),
        ForgottenItem(
            description="Accumulator Pre-charge Pressure Verification",
            related_operations=["drilling", "workover"],
            severity=RiskLevel.HIGH,
            recommended_action="Check BOP accumulator pre-charge pressures and fluid levels each tour",
            reference="API RP 53"
        ),
        ForgottenItem(
            description="Mud Gas Separator (MGS) Capacity Verification",
            related_operations=["drilling"],
            severity=RiskLevel.HIGH,
            recommended_action="Verify MGS is properly sized and functional; check vent line routing and capacity",
            reference="API RP 53"
        ),
        ForgottenItem(
            description="Stuck Pipe Drill / Contingency Practice",
            related_operations=["drilling", "tripping"],
            severity=RiskLevel.MEDIUM,
            recommended_action="Brief crew on stuck pipe procedures; practice jarring drill if jars are in string",
            reference="Company Stuck Pipe Procedure"
        ),
        ForgottenItem(
            description="Verify Kill Sheet Calculations Before Each Section",
            related_operations=["drilling"],
            severity=RiskLevel.HIGH,
            recommended_action="Complete and verify kill sheet with current well data at start of each section and shift change",
            reference="Well Control SOPs"
        ),
        ForgottenItem(
            description="Flow Check Before and After Connections",
            related_operations=["drilling"],
            severity=RiskLevel.MEDIUM,
            recommended_action="Monitor flow for 5 minutes before breaking connection in critical zones",
            reference="Well Control SOPs"
        ),
        ForgottenItem(
            description="Space-Out Drill for Subsea Operations",
            related_operations=["drilling"],
            severity=RiskLevel.HIGH,
            recommended_action="Verify correct tool joint space-out relative to BOP rams; mark pipe accordingly",
            reference="API RP 53 - Subsea"
        ),
        ForgottenItem(
            description="Verify Thread Compound Application on Casing",
            related_operations=["casing_running"],
            severity=RiskLevel.MEDIUM,
            recommended_action="Ensure correct thread compound type and application per manufacturer recommendation",
            reference="API RP 5C1"
        ),
        ForgottenItem(
            description="Cement Plug Bump Pressure Verification",
            related_operations=["cementing"],
            severity=RiskLevel.MEDIUM,
            recommended_action="Calculate and verify expected bump pressure; do not exceed casing burst",
            reference="Cementing Program"
        ),
        ForgottenItem(
            description="Wellhead Pressure Rating Verification for Well Test",
            related_operations=["well_testing"],
            severity=RiskLevel.CRITICAL,
            recommended_action="Verify all surface well test equipment rated for maximum anticipated pressure and H2S if applicable",
            reference="API RP 6A, Well Test Procedure"
        ),
        ForgottenItem(
            description="Corrosion Coupon Installation in Completion",
            related_operations=["completion"],
            severity=RiskLevel.LOW,
            recommended_action="Install corrosion coupons in completion string for future corrosion rate evaluation",
            reference="NACE Standards"
        ),
        ForgottenItem(
            description="Perforation Gun Arming Safety Checks",
            related_operations=["perforation"],
            severity=RiskLevel.CRITICAL,
            recommended_action="Follow explosive handling safety procedure; verify all safety interlocks before arming guns",
            reference="API RP 67, Explosive Safety Manual"
        ),
        ForgottenItem(
            description="Contingency String (Backup) Equipment Available on Location",
            related_operations=["drilling", "fishing", "casing_running", "completion"],
            severity=RiskLevel.MEDIUM,
            recommended_action="Ensure backup equipment (bit, BHA components, fishing tools) are on location for critical phases",
            reference="Well Planning Best Practices"
        ),
        ForgottenItem(
            description="Directional Survey Quality Check (Multi-Station vs Single Shot)",
            related_operations=["drilling"],
            severity=RiskLevel.MEDIUM,
            recommended_action="Verify survey quality with QA/QC checks; run gyro survey if magnetic interference suspected",
            reference="ISCWSA Standards"
        ),
        ForgottenItem(
            description="Well Barrier Diagram Update After Each Operation",
            related_operations=["drilling", "completion", "workover", "well_testing"],
            severity=RiskLevel.HIGH,
            recommended_action="Update well barrier schematic after each operation phase; verify two independent barriers",
            reference="NORSOK D-010, API RP 96"
        ),
    ]
    return items


# =============================================================================
# OPERATION KEYWORDS MAPPING
# =============================================================================

OPERATION_KEYWORDS = {
    "drilling": [
        "drill", "drilling", "rop", "wob", "rotary", "slide", "build section",
        "tangent", "lateral", "horizontal section", "vertical section", "mwd",
        "lwd", "mud motor", "rss", "directional", "pilot hole", "rat hole",
        "mouse hole", "spud", "kick off", "section"
    ],
    "tripping": [
        "trip", "tripping", "pooh", "rih", "pull out", "run in", "trip out",
        "trip in", "wiper trip", "short trip", "bit change", "change bit",
        "change bha", "bha change", "back ream"
    ],
    "casing_running": [
        "casing", "run casing", "running casing", "liner", "run liner",
        "liner hanger", "casing string", "conductor", "surface casing",
        "intermediate casing", "production casing", "casing running"
    ],
    "cementing": [
        "cement", "cementing", "cement job", "squeeze", "cement squeeze",
        "woc", "wait on cement", "cement plug", "balanced plug", "shoe track",
        "primary cement", "remedial cement"
    ],
    "completion": [
        "completion", "ssd", "sliding sleeve", "icd", "packer", "set packer",
        "tubing hanger", "xmas tree", "christmas tree", "gravel pack",
        "sand screen", "sand control", "esp", "gas lift", "artificial lift",
        "upper completion", "lower completion", "intelligent completion",
        "open ssd", "close ssd", "install packer"
    ],
    "perforation": [
        "perf", "perforation", "perforate", "gun", "tcp", "wireline perf",
        "tubing conveyed", "shoot", "charges", "shaped charge", "jet perf"
    ],
    "well_testing": [
        "well test", "dst", "flow test", "buildup", "drawdown", "cleanup",
        "flow period", "shut in", "extended well test", "ewt", "flowback",
        "test separator", "well testing"
    ],
    "fishing": [
        "fish", "fishing", "overshot", "spear", "junk basket", "milling",
        "mill", "back off", "back-off", "free point", "jarring", "impression block",
        "washover", "sidetrack"
    ],
    "workover": [
        "workover", "work over", "recompletion", "well intervention",
        "kill well", "well kill", "recomplete", "stimulation", "acid job",
        "frac", "fracture", "hydraulic fracturing", "coiled tubing", "ct job"
    ],
    "slickline": [
        "slickline", "wireline", "e-line", "eline", "logging", "gauge",
        "shifting tool", "plug", "bridge plug", "lock mandrel"
    ],
    "tubing": [
        "tubing", "production tubing", "tubing string", "pull tubing",
        "run tubing", "tubing hanger"
    ],
    "logging": [
        "log", "logging", "open hole log", "cased hole log", "cblt",
        "gamma ray", "resistivity", "density", "neutron", "sonic",
        "caliper", "formation evaluation"
    ],
}


# =============================================================================
# SEQUENCE PARSER
# =============================================================================

class SequenceParser:
    """Parses user-entered drilling sequence and maps to operation types."""

    def __init__(self):
        self.keywords = OPERATION_KEYWORDS

    def parse_line(self, line: str) -> Optional[str]:
        """Parse a single line and return the operation type."""
        line_lower = line.strip().lower()
        if not line_lower:
            return None

        best_match = None
        best_score = 0

        for op_type, keywords in self.keywords.items():
            score = 0
            for kw in keywords:
                if kw in line_lower:
                    score += len(kw)
            if score > best_score:
                best_score = score
                best_match = op_type

        return best_match if best_score > 0 else None

    def parse_sequence(self, text: str) -> List[Dict[str, str]]:
        """Parse the full sequence text and return list of operations."""
        results = []
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            op_type = self.parse_line(line)
            results.append({
                "description": line,
                "operation_type": op_type
            })
        return results


# =============================================================================
# ANALYSIS ENGINE
# =============================================================================

class AnalysisEngine:
    """Core engine for risk analysis and contingency planning."""

    def __init__(self):
        self.risks = build_risk_database()
        self.forgotten_items = build_forgotten_items()
        self.parser = SequenceParser()

    def analyze(self, sequence_text: str) -> Dict[str, Any]:
        """Perform full analysis on the given sequence."""
        # Parse the sequence
        operations = self.parser.parse_sequence(sequence_text)
        identified_types = set()
        unrecognized = []

        for op in operations:
            if op["operation_type"]:
                identified_types.add(op["operation_type"])
            else:
                unrecognized.append(op["description"])

        # Get risks for identified operations
        matched_risks = []
        for risk in self.risks:
            for op_type in identified_types:
                if op_type in risk.related_operations:
                    if risk not in matched_risks:
                        matched_risks.append(risk)

        # Sort risks by severity and probability
        matched_risks.sort(
            key=lambda r: (SEVERITY_ORDER[r.severity], -r.probability)
        )

        # Get forgotten items
        matched_forgotten = []
        for item in self.forgotten_items:
            for op_type in identified_types:
                if op_type in item.related_operations:
                    if item not in matched_forgotten:
                        matched_forgotten.append(item)

        # Calculate summary statistics
        severity_counts = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 0,
            RiskLevel.MEDIUM: 0,
            RiskLevel.LOW: 0,
        }
        total_npt = 0
        for risk in matched_risks:
            severity_counts[risk.severity] += 1
            total_npt += risk.npt_hours * risk.probability

        # Build summary
        summary = self._build_summary(
            operations, identified_types, matched_risks,
            matched_forgotten, severity_counts, total_npt, unrecognized
        )

        return {
            "operations": operations,
            "identified_types": list(identified_types),
            "unrecognized": unrecognized,
            "risks": matched_risks,
            "forgotten_items": matched_forgotten,
            "severity_counts": severity_counts,
            "total_expected_npt": total_npt,
            "summary": summary
        }

    def _build_summary(self, operations, identified_types, risks,
                       forgotten, severity_counts, total_npt, unrecognized):
        """Build formatted summary text."""
        lines = []
        lines.append("=" * 70)
        lines.append("DRILLING RISK ANALYSIS & CONTINGENCY PLANNING REPORT")
        lines.append("=" * 70)
        lines.append("")

        lines.append("OPERATIONS ANALYZED:")
        lines.append("-" * 40)
        for op in operations:
            status = f"[{op['operation_type'].upper()}]" if op['operation_type'] else "[UNRECOGNIZED]"
            lines.append(f"  • {op['description']}  {status}")
        lines.append("")

        if unrecognized:
            lines.append("⚠ UNRECOGNIZED OPERATIONS:")
            for u in unrecognized:
                lines.append(f"  • {u}")
            lines.append("")

        lines.append("RISK SEVERITY DISTRIBUTION:")
        lines.append("-" * 40)
        lines.append(f"  🔴 Critical:  {severity_counts[RiskLevel.CRITICAL]}")
        lines.append(f"  🟠 High:      {severity_counts[RiskLevel.HIGH]}")
        lines.append(f"  🟡 Medium:    {severity_counts[RiskLevel.MEDIUM]}")
        lines.append(f"  🟢 Low:       {severity_counts[RiskLevel.LOW]}")
        lines.append(f"  Total Risks:  {sum(severity_counts.values())}")
        lines.append("")

        lines.append(f"EXPECTED NPT (Probability-Weighted): {total_npt:.1f} hours")
        lines.append("")

        lines.append("TOP PRIORITY ACTIONS:")
        lines.append("-" * 40)
        priority_num = 1
        for risk in risks[:10]:
            lines.append(f"  {priority_num}. [{risk.severity.value}] {risk.problem}")
            lines.append(f"     Category: {risk.category}")
            lines.append(f"     Probability: {risk.probability:.0%}, NPT: {risk.npt_hours}h")
            if risk.contingency_plans:
                lines.append(f"     Primary Action: {risk.contingency_plans[0].action[:100]}...")
            priority_num += 1
        lines.append("")

        lines.append(f"FORGOTTEN ITEMS / BEST PRACTICES CHECKLIST: {len(forgotten)} items")
        lines.append("-" * 40)
        for item in forgotten[:15]:
            lines.append(f"  ☐ [{item.severity.value}] {item.description}")
            lines.append(f"    Action: {item.recommended_action[:100]}...")
            if item.reference:
                lines.append(f"    Ref: {item.reference}")
        lines.append("")

        lines.append("=" * 70)
        lines.append("END OF REPORT")
        lines.append("=" * 70)

        return "\n".join(lines)


# =============================================================================
# AI BACKEND INTEGRATION
# =============================================================================

class AIBackend:
    """Handles AI analysis using various backends."""

    @staticmethod
    def build_prompt(analysis_results: Dict) -> str:
        """Build a comprehensive prompt for the AI."""
        risks = analysis_results["risks"]
        forgotten = analysis_results["forgotten_items"]
        ops = analysis_results["operations"]

        prompt = """You are an expert drilling and well operations engineer with 30+ years of experience.

I have the following drilling/workover operation sequence:
"""
        for op in ops:
            prompt += f"- {op['description']} (Type: {op['operation_type'] or 'Unrecognized'})\n"

        prompt += f"""
My analysis has identified {len(risks)} potential risks:
"""
        for r in risks[:20]:
            prompt += f"- [{r.severity.value}] {r.problem} (Probability: {r.probability:.0%}, NPT: {r.npt_hours}h)\n"

        prompt += f"""
And {len(forgotten)} forgotten items / best practice reminders.

Please provide:
1. SUPPLEMENTARY RISK ANALYSIS: Identify any hidden or interdependent risks that may have been missed in the standard analysis. Think about cascading failures, compound risks, and interactions between operations.

2. OPERATIONAL SEQUENCE OPTIMIZATION: Are there any steps in the sequence that should be reordered, added, or modified to reduce overall risk?

3. FORGOTTEN OPERATIONS: Based on the sequence provided, are there any critical operations or steps that appear to be missing? (e.g., pressure tests, barrier verifications, clean-up circulations, etc.)

4. PRACTICAL RECOMMENDATIONS: Provide specific, actionable recommendations for the highest-risk items. Include lessons learned from real drilling incidents.

5. INDUSTRY BEST PRACTICES: Reference relevant API, IADC, NORSOK, or other industry standards that should be followed for this operation sequence.

6. COST-RISK OPTIMIZATION: Suggest ways to reduce NPT risk while being cost-effective.

Please be specific, practical, and reference real-world drilling engineering knowledge.
"""
        return prompt

    @staticmethod
    def query_gemini(prompt: str, api_key: str) -> str:
        """Query Google Gemini API."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            return response.text
        except ImportError:
            return "Error: google-generativeai package not installed.\nInstall with: pip install google-generativeai"
        except Exception as e:
            return f"Error querying Gemini API: {str(e)}"

    @staticmethod
    def query_ollama(prompt: str) -> str:
        """Query local Ollama instance."""
        try:
            import urllib.request
            import json as json_mod

            data = json_mod.dumps({
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            }).encode('utf-8')

            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=data,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=120) as response:
                result = json_mod.loads(response.read().decode('utf-8'))
                return result.get("response", "No response received from Ollama")

        except Exception as e:
            return f"Error querying Ollama (ensure Ollama is running with llama2 model):\n{str(e)}"

    @staticmethod
    def query_huggingface(prompt: str, api_key: str) -> str:
        """Query HuggingFace Inference API."""
        try:
            import urllib.request
            import json as json_mod

            data = json_mod.dumps({
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 2000,
                    "temperature": 0.7
                }
            }).encode('utf-8')

            req = urllib.request.Request(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
            )

            with urllib.request.urlopen(req, timeout=120) as response:
                result = json_mod.loads(response.read().decode('utf-8'))
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "No text generated")
                return str(result)

        except Exception as e:
            return f"Error querying HuggingFace API:\n{str(e)}"


# =============================================================================
# WORKER THREADS
# =============================================================================

class AnalysisWorker(QThread):
    """Background worker thread for analysis."""
    progress = Signal(int)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, sequence_text: str):
        super().__init__()
        self.sequence_text = sequence_text

    def run(self):
        try:
            self.progress.emit(10)
            engine = AnalysisEngine()
            self.progress.emit(30)
            results = engine.analyze(self.sequence_text)
            self.progress.emit(90)
            self.progress.emit(100)
            self.finished.emit(results)
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            self.error.emit(str(e))


class AIWorker(QThread):
    """Background worker thread for AI analysis."""
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, prompt: str, backend: str, api_key: str):
        super().__init__()
        self.prompt = prompt
        self.backend = backend
        self.api_key = api_key

    def run(self):
        try:
            self.progress.emit(20)

            if self.backend == "Gemini":
                result = AIBackend.query_gemini(self.prompt, self.api_key)
            elif self.backend == "Ollama":
                result = AIBackend.query_ollama(self.prompt)
            elif self.backend == "HuggingFace":
                result = AIBackend.query_huggingface(self.prompt, self.api_key)
            else:
                result = "No AI backend selected."

            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            self.error.emit(str(e))


# =============================================================================
# UNRECOGNIZED OPERATION DIALOG
# =============================================================================

class UnrecognizedDialog(QDialog):
    """Dialog for user to specify unrecognized operation types."""

    def __init__(self, unrecognized_ops: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Unrecognized Operations")
        self.setMinimumWidth(550)
        self.results = {}

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "The following operations were not automatically recognized.\n"
            "Please select the correct operation type for each:"
        ))

        self.combos = {}
        op_types = ["drilling", "tripping", "casing_running", "cementing",
                     "completion", "perforation", "well_testing", "fishing",
                     "workover", "slickline", "tubing", "logging", "other"]

        form = QFormLayout()
        for op_desc in unrecognized_ops:
            combo = QComboBox()
            combo.addItems(op_types)
            combo.setCurrentText("other")
            form.addRow(QLabel(f'"{op_desc}"'), combo)
            self.combos[op_desc] = combo

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_results(self) -> Dict[str, str]:
        """Return user-selected operation types."""
        return {desc: combo.currentText() for desc, combo in self.combos.items()}


# =============================================================================
# MAIN WINDOW
# =============================================================================

STYLESHEET = """
QMainWindow {
    background-color: #f0f2f5;
}
QGroupBox {
    font-weight: bold;
    border: 2px solid #cccccc;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    background-color: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px;
    color: #1a3a5c;
}
QTabWidget::pane {
    border: 2px solid #cccccc;
    border-radius: 8px;
    background-color: #ffffff;
}
QTabBar::tab {
    background-color: #e0e4e8;
    padding: 10px 20px;
    margin-right: 3px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: bold;
    min-width: 120px;
}
QTabBar::tab:selected {
    background-color: #1a3a5c;
    color: white;
}
QTabBar::tab:hover:!selected {
    background-color: #c0c8d0;
}
QPushButton {
    background-color: #1a3a5c;
    color: white;
    border: none;
    padding: 12px 28px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #2a5a8c;
}
QPushButton:pressed {
    background-color: #0f2540;
}
QPushButton:disabled {
    background-color: #999999;
}
QTextEdit {
    border: 2px solid #cccccc;
    border-radius: 6px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    background-color: #fafbfc;
}
QComboBox {
    padding: 8px 12px;
    border: 2px solid #cccccc;
    border-radius: 6px;
    background-color: white;
    min-width: 150px;
}
QLineEdit {
    padding: 8px 12px;
    border: 2px solid #cccccc;
    border-radius: 6px;
    background-color: white;
}
QProgressBar {
    border: 2px solid #cccccc;
    border-radius: 6px;
    text-align: center;
    font-weight: bold;
    background-color: #e8e8e8;
}
QProgressBar::chunk {
    background-color: #1a3a5c;
    border-radius: 4px;
}
QTableWidget {
    border: 1px solid #cccccc;
    gridline-color: #e0e0e0;
    background-color: white;
    alternate-background-color: #f8f9fa;
    selection-background-color: #1a3a5c;
    selection-color: white;
    font-size: 12px;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background-color: #1a3a5c;
    color: white;
    padding: 8px;
    border: 1px solid #15304d;
    font-weight: bold;
    font-size: 12px;
}
QLabel {
    color: #333333;
}
"""


class MainWindow(QMainWindow):
    """Main application window for Drilling Risk Analysis."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drilling Risk Analysis & Contingency Planning System")
        self.setMinimumSize(1300, 850)
        self.setStyleSheet(STYLESHEET)

        self.analysis_results = None
        self.analysis_worker = None
        self.ai_worker = None

        self._build_ui()
        logger.info("Application initialized successfully")

    def _build_ui(self):
        """Build the complete user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Splitter: Input on left, Results on right
        splitter = QSplitter(Qt.Horizontal)

        # Input panel
        input_panel = self._create_input_panel()
        splitter.addWidget(input_panel)

        # Results panel
        results_panel = self._create_results_panel()
        splitter.addWidget(results_panel)

        splitter.setSizes([450, 850])
        main_layout.addWidget(splitter, 1)

    def _create_header(self) -> QFrame:
        """Create the application header."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f2540, stop:1 #1a3a5c
                );
                border-radius: 10px;
                padding: 15px;
            }
        """)
        layout = QHBoxLayout(header)

        title_label = QLabel("⛽ Drilling Risk Analysis & Contingency Planning")
        title_label.setStyleSheet("""
            color: white;
            font-size: 22px;
            font-weight: bold;
        """)
        layout.addWidget(title_label)

        layout.addStretch()

        subtitle = QLabel("Expert System + AI-Powered Analysis")
        subtitle.setStyleSheet("""
            color: #a0c4e8;
            font-size: 14px;
            font-style: italic;
        """)
        layout.addWidget(subtitle)

        return header

    def _create_input_panel(self) -> QWidget:
        """Create the input panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)

        # Sequence input
        seq_group = QGroupBox("📋 Operation Sequence")
        seq_layout = QVBoxLayout(seq_group)

        seq_label = QLabel("Enter drilling/workover operations (one per line):")
        seq_label.setStyleSheet("font-size: 13px; color: #555;")
        seq_layout.addWidget(seq_label)

        self.sequence_input = QTextEdit()
        self.sequence_input.setPlaceholderText(
            "Example:\n"
            "Drilling 12-1/4 section\n"
            "Tripping out to change bit\n"
            "Running 9-5/8 casing\n"
            "Cementing\n"
            "Drilling 8-1/2 section\n"
            "POOH for logging\n"
            "Running 7 liner\n"
            "Cementing liner\n"
            "Completion run with packer\n"
            "Opening SSD with slickline\n"
            "Perforation\n"
            "Well testing"
        )
        self.sequence_input.setMinimumHeight(220)
        seq_layout.addWidget(self.sequence_input)
        layout.addWidget(seq_group)

        # AI Backend selection
        ai_group = QGroupBox("🤖 AI Analysis Backend")
        ai_layout = QVBoxLayout(ai_group)

        backend_row = QHBoxLayout()
        backend_row.addWidget(QLabel("Backend:"))
        self.ai_combo = QComboBox()
        self.ai_combo.addItems(["None", "Gemini", "Ollama", "HuggingFace"])
        self.ai_combo.currentTextChanged.connect(self._on_ai_backend_changed)
        backend_row.addWidget(self.ai_combo)
        ai_layout.addLayout(backend_row)

        api_row = QHBoxLayout()
        api_row.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter API key (if required)")
        self.api_key_input.setEnabled(False)
        api_row.addWidget(self.api_key_input)
        ai_layout.addLayout(api_row)

        layout.addWidget(ai_group)

        # Analyze button and progress
        self.analyze_btn = QPushButton("🔍 Analyze Sequence")
        self.analyze_btn.setMinimumHeight(50)
        self.analyze_btn.clicked.connect(self._start_analysis)
        layout.addWidget(self.analyze_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% - Ready")
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready. Enter operation sequence and click Analyze.")
        self.status_label.setStyleSheet("color: #666; font-style: italic; font-size: 12px;")
        layout.addWidget(self.status_label)

        layout.addStretch()
        return panel

    def _create_results_panel(self) -> QWidget:
        """Create the results panel with tabs."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.tabs = QTabWidget()

        # Tab 1: Risk Analysis
        self.risk_table = QTableWidget()
        self.risk_table.setColumnCount(8)
        self.risk_table.setHorizontalHeaderLabels([
            "Problem", "Severity", "Probability", "NPT (hrs)",
            "Category", "Early Warning Signs", "Root Causes", "Priority"
        ])
        self.risk_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.risk_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.risk_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.risk_table.setAlternatingRowColors(True)
        self.risk_table.setWordWrap(True)
        self.risk_table.verticalHeader().setDefaultSectionSize(60)
        self.tabs.addTab(self.risk_table, "⚠️ Risk Analysis")

        # Tab 2: Contingency Plans
        self.contingency_table = QTableWidget()
        self.contingency_table.setColumnCount(6)
        self.contingency_table.setHorizontalHeaderLabels([
            "Problem", "Priority", "Contingency Action",
            "Success Prob.", "Duration (hrs)", "Cost (USD)"
        ])
        self.contingency_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.contingency_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.contingency_table.setAlternatingRowColors(True)
        self.contingency_table.setWordWrap(True)
        self.contingency_table.verticalHeader().setDefaultSectionSize(60)
        self.tabs.addTab(self.contingency_table, "📋 Contingency Plans")

        # Tab 3: Forgotten Items Checklist
        self.forgotten_table = QTableWidget()
        self.forgotten_table.setColumnCount(4)
        self.forgotten_table.setHorizontalHeaderLabels([
            "✓", "Description", "Severity", "Recommended Action"
        ])
        self.forgotten_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.forgotten_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.forgotten_table.setColumnWidth(0, 40)
        self.forgotten_table.setAlternatingRowColors(True)
        self.forgotten_table.setWordWrap(True)
        self.forgotten_table.verticalHeader().setDefaultSectionSize(55)
        self.tabs.addTab(self.forgotten_table, "☑️ Forgotten Items")

        # Tab 4: Summary & Action Plan
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.6;
                padding: 15px;
                background-color: #fafbfc;
            }
        """)
        self.tabs.addTab(self.summary_text, "📊 Summary & Action Plan")

        # Tab 5: AI Insights
        self.ai_text = QTextEdit()
        self.ai_text.setReadOnly(True)
        self.ai_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                line-height: 1.6;
                padding: 15px;
                background-color: #f8f9fa;
            }
        """)
        self.ai_text.setPlaceholderText("AI analysis results will appear here after analysis...\n\nSelect an AI backend (Gemini, Ollama, or HuggingFace) to enable AI-powered insights.")
        self.tabs.addTab(self.ai_text, "🧠 AI Insights")

        layout.addWidget(self.tabs)
        return panel

    def _on_ai_backend_changed(self, backend: str):
        """Handle AI backend selection change."""
        needs_key = backend in ("Gemini", "HuggingFace")
        self.api_key_input.setEnabled(needs_key)
        if not needs_key:
            self.api_key_input.clear()

    def _start_analysis(self):
        """Start the analysis process."""
        sequence_text = self.sequence_input.toPlainText().strip()
        if not sequence_text:
            QMessageBox.warning(
                self, "Input Required",
                "Please enter at least one drilling/workover operation."
            )
            return

        # Validate minimum input
        lines = [l.strip() for l in sequence_text.split('\n') if l.strip()]
        if len(lines) < 1:
            QMessageBox.warning(
                self, "Input Required",
                "Please enter at least one operation step."
            )
            return

        # Check for unrecognized operations first
        parser = SequenceParser()
        ops = parser.parse_sequence(sequence_text)
        unrecognized = [op["description"] for op in ops if op["operation_type"] is None]

        if unrecognized:
            dialog = UnrecognizedDialog(unrecognized, self)
            if dialog.exec() == QDialog.Accepted:
                user_mappings = dialog.get_results()
                # Rebuild sequence with user mappings
                new_lines = []
                for op in ops:
                    if op["operation_type"] is None and op["description"] in user_mappings:
                        mapped_type = user_mappings[op["description"]]
                        if mapped_type != "other":
                            # Add a keyword hint to the line so it gets recognized
                            new_lines.append(f"{op['description']} [{mapped_type}]")
                            # Update the keywords temporarily
                            if mapped_type in OPERATION_KEYWORDS:
                                # Add the exact description as a keyword match
                                OPERATION_KEYWORDS[mapped_type].append(op['description'].lower())
                        else:
                            new_lines.append(op["description"])
                    else:
                        new_lines.append(op["description"])
                sequence_text = "\n".join(new_lines)
            else:
                return  # User cancelled

        self.analyze_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% - Analyzing...")
        self.status_label.setText("🔄 Analysis in progress...")

        # Start background analysis
        self.analysis_worker = AnalysisWorker(sequence_text)
        self.analysis_worker.progress.connect(self._update_progress)
        self.analysis_worker.finished.connect(self._on_analysis_complete)
        self.analysis_worker.error.connect(self._on_analysis_error)
        self.analysis_worker.start()

    def _update_progress(self, value: int):
        """Update progress bar."""
        self.progress_bar.setValue(value)

    def _on_analysis_complete(self, results: Dict):
        """Handle analysis completion."""
        self.analysis_results = results
        self._populate_risk_table(results["risks"])
        self._populate_contingency_table(results["risks"])
        self._populate_forgotten_table(results["forgotten_items"])
        self.summary_text.setPlainText(results["summary"])

        self.progress_bar.setFormat("Analysis Complete!")
        self.status_label.setText(
            f"✅ Analysis complete: {len(results['risks'])} risks identified, "
            f"{len(results['forgotten_items'])} best-practice reminders"
        )

        # Start AI analysis if backend is selected
        ai_backend = self.ai_combo.currentText()
        if ai_backend != "None":
            self._start_ai_analysis(results, ai_backend)
        else:
            self.analyze_btn.setEnabled(True)
            self.ai_text.setPlainText("No AI backend selected.\n\nSelect Gemini, Ollama, or HuggingFace from the AI Backend dropdown and re-analyze to get AI-powered insights.")

    def _on_analysis_error(self, error_msg: str):
        """Handle analysis error."""
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setFormat("Error!")
        self.status_label.setText(f"❌ Error: {error_msg}")
        QMessageBox.critical(self, "Analysis Error", error_msg)

    def _start_ai_analysis(self, results: Dict, backend: str):
        """Start AI analysis in background thread."""
        api_key = self.api_key_input.text().strip()

        if backend in ("Gemini", "HuggingFace") and not api_key:
            QMessageBox.warning(
                self, "API Key Required",
                f"Please enter your {backend} API key."
            )
            self.analyze_btn.setEnabled(True)
            return

        self.ai_text.setPlainText(f"🔄 Querying {backend} AI backend...\nPlease wait...")
        self.status_label.setText(f"🤖 Querying {backend} AI...")
        self.progress_bar.setFormat(f"AI Analysis ({backend})...")
        self.progress_bar.setValue(50)

        prompt = AIBackend.build_prompt(results)

        self.ai_worker = AIWorker(prompt, backend, api_key)
        self.ai_worker.progress.connect(self._update_progress)
        self.ai_worker.finished.connect(self._on_ai_complete)
        self.ai_worker.error.connect(self._on_ai_error)
        self.ai_worker.start()

    def _on_ai_complete(self, result: str):
        """Handle AI analysis completion."""
        self.ai_text.setPlainText(result)
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("Complete!")
        self.status_label.setText("✅ Analysis and AI insights complete!")
        self.tabs.setCurrentIndex(4)  # Switch to AI tab

    def _on_ai_error(self, error_msg: str):
        """Handle AI analysis error."""
        self.ai_text.setPlainText(f"❌ AI Error:\n{error_msg}")
        self.analyze_btn.setEnabled(True)
        self.progress_bar.setFormat("AI Error - Base Analysis Complete")
        self.status_label.setText(f"⚠️ AI error (base analysis is still valid): {error_msg}")

    def _populate_risk_table(self, risks: List[OperationRisk]):
        """Populate the risk analysis table."""
        self.risk_table.setRowCount(len(risks))

        for row, risk in enumerate(risks):
            # Problem
            item = QTableWidgetItem(risk.problem)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.risk_table.setItem(row, 0, item)

            # Severity
            sev_item = QTableWidgetItem(risk.severity.value)
            sev_item.setBackground(QBrush(SEVERITY_COLORS[risk.severity]))
            if risk.severity in (RiskLevel.CRITICAL, RiskLevel.HIGH):
                sev_item.setForeground(QBrush(QColor(255, 255, 255)))
            else:
                sev_item.setForeground(QBrush(QColor(0, 0, 0)))
            sev_item.setTextAlignment(Qt.AlignCenter)
            sev_item.setFlags(sev_item.flags() & ~Qt.ItemIsEditable)
            self.risk_table.setItem(row, 1, sev_item)

            # Probability
            prob_item = QTableWidgetItem(f"{risk.probability:.0%}")
            prob_item.setTextAlignment(Qt.AlignCenter)
            prob_item.setFlags(prob_item.flags() & ~Qt.ItemIsEditable)
            self.risk_table.setItem(row, 2, prob_item)

            # NPT
            npt_item = QTableWidgetItem(f"{risk.npt_hours:.0f}")
            npt_item.setTextAlignment(Qt.AlignCenter)
            npt_item.setFlags(npt_item.flags() & ~Qt.ItemIsEditable)
            self.risk_table.setItem(row, 3, npt_item)

            # Category
            cat_item = QTableWidgetItem(risk.category)
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsEditable)
            self.risk_table.setItem(row, 4, cat_item)

            # Early Warning Signs
            signs_text = "\n".join(f"• {s}" for s in risk.early_warning_signs[:3])
            if len(risk.early_warning_signs) > 3:
                signs_text += f"\n  +{len(risk.early_warning_signs) - 3} more..."
            signs_item = QTableWidgetItem(signs_text)
            signs_item.setFlags(signs_item.flags() & ~Qt.ItemIsEditable)
            self.risk_table.setItem(row, 5, signs_item)

            # Root Causes
            causes_text = "\n".join(f"• {c}" for c in risk.root_causes[:3])
            if len(risk.root_causes) > 3:
                causes_text += f"\n  +{len(risk.root_causes) - 3} more..."
            causes_item = QTableWidgetItem(causes_text)
            causes_item.setFlags(causes_item.flags() & ~Qt.ItemIsEditable)
            self.risk_table.setItem(row, 6, causes_item)

            # Priority
            priority = row + 1
            pri_item = QTableWidgetItem(str(priority))
            pri_item.setTextAlignment(Qt.AlignCenter)
            pri_item.setFont(QFont("Arial", 12, QFont.Bold))
            pri_item.setFlags(pri_item.flags() & ~Qt.ItemIsEditable)
            if priority <= 3:
                pri_item.setBackground(QBrush(QColor(220, 53, 69)))
                pri_item.setForeground(QBrush(QColor(255, 255, 255)))
            elif priority <= 8:
                pri_item.setBackground(QBrush(QColor(255, 193, 7)))
            self.risk_table.setItem(row, 7, pri_item)

        self.risk_table.resizeRowsToContents()

    def _populate_contingency_table(self, risks: List[OperationRisk]):
        """Populate the contingency plans table."""
        rows = []
        for risk in risks:
            for plan in risk.contingency_plans:
                rows.append((risk.problem, plan))

        self.contingency_table.setRowCount(len(rows))

        for row, (problem, plan) in enumerate(rows):
            # Problem
            item = QTableWidgetItem(problem)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.contingency_table.setItem(row, 0, item)

            # Priority
            pri_item = QTableWidgetItem(str(plan.priority))
            pri_item.setTextAlignment(Qt.AlignCenter)
            pri_item.setFont(QFont("Arial", 11, QFont.Bold))
            if plan.priority == 1:
                pri_item.setBackground(QBrush(QColor(40, 167, 69)))
                pri_item.setForeground(QBrush(QColor(255, 255, 255)))
            elif plan.priority == 2:
                pri_item.setBackground(QBrush(QColor(255, 193, 7)))
            else:
                pri_item.setBackground(QBrush(QColor(255, 140, 0)))
                pri_item.setForeground(QBrush(QColor(255, 255, 255)))
            pri_item.setFlags(pri_item.flags() & ~Qt.ItemIsEditable)
            self.contingency_table.setItem(row, 1, pri_item)

            # Action
            action_item = QTableWidgetItem(plan.action)
            action_item.setFlags(action_item.flags() & ~Qt.ItemIsEditable)
            self.contingency_table.setItem(row, 2, action_item)

            # Success probability
            prob_item = QTableWidgetItem(f"{plan.success_probability:.0%}")
            prob_item.setTextAlignment(Qt.AlignCenter)
            if plan.success_probability >= 0.80:
                prob_item.setBackground(QBrush(QColor(40, 167, 69)))
                prob_item.setForeground(QBrush(QColor(255, 255, 255)))
            elif plan.success_probability >= 0.60:
                prob_item.setBackground(QBrush(QColor(255, 193, 7)))
            else:
                prob_item.setBackground(QBrush(QColor(220, 53, 69)))
                prob_item.setForeground(QBrush(QColor(255, 255, 255)))
            prob_item.setFlags(prob_item.flags() & ~Qt.ItemIsEditable)
            self.contingency_table.setItem(row, 3, prob_item)

            # Duration
            dur_item = QTableWidgetItem(f"{plan.duration_hours:.1f}")
            dur_item.setTextAlignment(Qt.AlignCenter)
            dur_item.setFlags(dur_item.flags() & ~Qt.ItemIsEditable)
            self.contingency_table.setItem(row, 4, dur_item)

            # Cost
            cost_item = QTableWidgetItem(f"${plan.estimated_cost_usd:,.0f}")
            cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            cost_item.setFlags(cost_item.flags() & ~Qt.ItemIsEditable)
            self.contingency_table.setItem(row, 5, cost_item)

        self.contingency_table.resizeRowsToContents()

    def _populate_forgotten_table(self, items: List[ForgottenItem]):
        """Populate the forgotten items checklist table."""
        self.forgotten_table.setRowCount(len(items))

        for row, item in enumerate(items):
            # Checkbox
            cb_widget = QWidget()
            cb_layout = QHBoxLayout(cb_widget)
            cb_layout.setAlignment(Qt.AlignCenter)
            cb_layout.setContentsMargins(0, 0, 0, 0)
            checkbox = QCheckBox()
            checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")
            cb_layout.addWidget(checkbox)
            self.forgotten_table.setCellWidget(row, 0, cb_widget)

            # Description
            desc_item = QTableWidgetItem(item.description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            if item.reference:
                desc_item.setToolTip(f"Reference: {item.reference}")
            self.forgotten_table.setItem(row, 1, desc_item)

            # Severity
            sev_item = QTableWidgetItem(item.severity.value)
            sev_item.setBackground(QBrush(SEVERITY_COLORS[item.severity]))
            if item.severity in (RiskLevel.CRITICAL, RiskLevel.HIGH):
                sev_item.setForeground(QBrush(QColor(255, 255, 255)))
            sev_item.setTextAlignment(Qt.AlignCenter)
            sev_item.setFlags(sev_item.flags() & ~Qt.ItemIsEditable)
            self.forgotten_table.setItem(row, 2, sev_item)

            # Recommended Action
            action_item = QTableWidgetItem(item.recommended_action)
            action_item.setFlags(action_item.flags() & ~Qt.ItemIsEditable)
            self.forgotten_table.setItem(row, 3, action_item)

        self.forgotten_table.resizeRowsToContents()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()