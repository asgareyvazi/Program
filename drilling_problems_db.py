# ============================================================================
# DRILLING PROBLEMS DATABASE — prevention & cure knowledge base
# File: drilling_problems_db.py
# A strong, general knowledge base of drilling problems:
#   - symptoms (علائم), causes (علل), prevention (پیشگیری),
#     remedies (راه‌حل‌ها به ترتیب اولویت), related library procedures
# Content grounded in the real problem documents added to the library
# (Drilling Problems, Borehole Problems, Drilling/Hole Problems, section
# 10 hole problems, deviation chapter, fishing, lost circulation, etc.)
# All general — no company/well names.
# ============================================================================

import json
import re
import sqlite3
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Optional

APP_DIR = Path.home() / ".drilling_program"
DEFAULT_DB = str(APP_DIR / "problems.db")

# library file numbers referenced by problems (keep as knowledge refs)
# (these numbers are internal-only, never printed to output docs)
LIB = {
    "drilling_problems": "263, 364",
    "borehole_problems": "295",
    "hole_problems": "363, 493",
    "deviation": "322",
    "gauge_problems": "246",
    "fishing": "363",
    "rig_problems": "462",
    "cement_problems": "310",
}


@dataclass
class DrillingProblem:
    code: str
    category: str
    name: str
    severity: str            # High / Medium / Low
    symptoms: List[str] = field(default_factory=list)
    causes: List[str] = field(default_factory=list)
    prevention: List[str] = field(default_factory=list)
    remedies: List[str] = field(default_factory=list)   # ordered by priority
    related_procedures: List[str] = field(default_factory=list)
    library_refs: List[str] = field(default_factory=list)


# ============================================================================
# KNOWLEDGE BASE — 35+ problems grounded in industry practice & library docs
# ============================================================================

PROBLEMS: List[DrillingProblem] = [

    # ============================================================ STUCK PIPE
    DrillingProblem(
        code="SP-01", category="Stuck Pipe", name="Differential Sticking",
        severity="High",
        symptoms=[
            "Pipe cannot be rotated or reciprocated but circulation is normal",
            "Stuck occurs after a period of no pipe movement (connections, logging, surveys)",
            "Overpull does not free the pipe; torque normal before sticking",
            "Usually occurs across permeable formations with thick filter cake",
        ],
        causes=[
            "High overbalance (mud hydrostatic >> formation pressure)",
            "Thick, high-friction filter cake across permeable zones",
            "Pipe left static against the wall for a long time",
            "High solids content / poor mud cake quality",
        ],
        prevention=[
            "Maintain minimum safe overbalance; keep ECD as low as practical",
            "Use low-fluid-loss mud with thin, slick, low-friction filter cake",
            "Keep pipe moving when possible (rotate/reciprocate during connections)",
            "Use pipe-racking / wiper trips; avoid long static periods",
            "Add lubricants / anti-stick additives to the mud",
            "Run stabilizers and spiral drill collars to reduce contact area",
            "Calculate and respect the 'safe static time' for the mud system",
        ],
        remedies=[
            "Attempt jarring with controlled upward/downward blows (fishing jar + accelerator)",
            "Spot a differential-sticking release agent (pipe-free / penetrating oil pill) across the stuck point",
            "Reduce mud weight if well conditions allow (lower hydrostatic pressure)",
            "Work the pipe with rotation + reciprocation after spotting the pill",
            "If pipe remains stuck, set a cement plug / free-point & back-off, then sidetrack",
        ],
        related_procedures=["Free Point & Back-off", "Jarring Operations", "Pipe-Free Pill Spotting"],
        library_refs=["263", "364"],
    ),
    DrillingProblem(
        code="SP-02", category="Stuck Pipe", name="Mechanical Sticking (Junk / Key Seat / Collapse)",
        severity="High",
        symptoms=[
            "Pipe stuck with loss of circulation or high torque first",
            "Stuck while RIH (junk/collapse) or while POOH (key seat / undergauge hole)",
            "Inability to rotate and/or reciprocate; circulation may be restricted",
            "Fill on bottom after tripping (collapse / caving)",
        ],
        causes=[
            "Junk in hole (bit cones, tools, debris) wedging the BHA",
            "Key seating in doglegs / ledges",
            "Hole collapse / caving of unstable formations",
            "Undergauge hole (swelling shales, salt creep)",
            "Cement / hard bridges from previous operations",
        ],
        prevention=[
            "Keep hole clean: adequate annular velocity, sweeps, wiper trips",
            "Minimize doglegs; use key-seat wipers when pulling through high-dogleg sections",
            "Maintain mud properties to control swelling shales (inhibitive system)",
            "Run undergauge stabilizers / string reamers in known problem intervals",
            "Catch junk early: magnets, junk baskets, boot baskets",
        ],
        remedies=[
            "Identify the stuck mechanism (rotation? circulation? both?)",
            "If key seat: rotate and work down, use key-seat wiper, spot lubricant",
            "If junk: mill / fish the obstruction (junk mill, boot basket, magnet)",
            "If collapsed hole: circulate heavy viscous pill, ream and condition hole",
            "Free point determination → back-off → fishing or sidetrack",
        ],
        related_procedures=["Fishing Operations", "Back-Off & Free Point", "Milling", "Hole Cleaning"],
        library_refs=["263", "364", "363"],
    ),
    DrillingProblem(
        code="SP-03", category="Stuck Pipe", name="Key Seating",
        severity="Medium",
        symptoms=[
            "Pipe becomes stuck while POOH at the same depth repeatedly",
            "Rotation usually possible, upward movement blocked",
            "Overpull releases after working down",
            "Occurs in doglegs with high build/turn rates",
        ],
        causes=[
            "Excessive dogleg severity — pipe wears a groove (key seat) in the wall",
            "Large-diameter BHA / tool joints pull into the groove",
            "Soft formations with hard stringers in doglegs",
        ],
        prevention=[
            "Design trajectory to minimize DLS (max 2-3°/30m in build sections)",
            "Use key-seat wipers / reamers when POOH through doglegs",
            "Rotate through high-DLS intervals while tripping out",
            "Monitor and record DLS from surveys; plan trips accordingly",
        ],
        remedies=[
            "Work the string down first (not up) to disengage from the seat",
            "Rotate while working; spot lubricant / pipe-free pill at the key-seat depth",
            "Ream down to bottom, then rotate and pull slowly through the zone",
            "If stuck: free-point, back-off, run key-seat wiper, then sidetrack if needed",
        ],
        related_procedures=["Back-Off & Free Point", "Directional Planning"],
        library_refs=["263", "364"],
    ),
    DrillingProblem(
        code="SP-04", category="Stuck Pipe", name="Stuck Pipe — General Response Sequence",
        severity="High",
        symptoms=[
            "Any stuck-pipe event: unable to move pipe as planned",
            "Record time, depth, conditions (rotation/circulation status)",
        ],
        causes=[
            "Differential, mechanical, key-seat or hole-collapse mechanisms (see SP-01..03)",
        ],
        prevention=[
            "Hole cleaning & mud program optimized per section",
            "Trip procedures: slow speeds through tight spots, ream, circulate",
            "Contingency: jars in BHA, string floats, safety valves, top drive",
        ],
        remedies=[
            "1) Stop; record; do NOT pull hard (may wedge further)",
            "2) Attempt rotation + circulation to establish returns",
            "3) Work pipe within safe limits (up/down with rotation)",
            "4) Spot pipe-free / penetrating pill across stuck point",
            "5) Jar with controlled blows (accelerator + jar)",
            "6) Free-point indicator → back-off at stuck point",
            "7) Fish (overshot, washover) or sidetrack after cement plug",
        ],
        related_procedures=["Free Point & Back-off", "Fishing", "Jarring", "Sidetrack"],
        library_refs=["263", "364", "363", "493"],
    ),

    # ===================================================== LOST CIRCULATION
    DrillingProblem(
        code="LC-01", category="Lost Circulation", name="Lost Circulation (Seepage to Total)",
        severity="High",
        symptoms=[
            "Mud tank volume drops without surface losses",
            "Partial to complete loss of returns (returns at shaker reduce/stop)",
            "Possible drop in mud level / gain in pit when connection gas or kick occurs",
            "Drilling breaks / ROP changes when entering loss zone",
        ],
        causes=[
            "Naturally fractured / vuggy formations (limestone, dolomite)",
            "Unconsolidated / gravel formations (high permeability)",
            "Excessive ECD / fracture gradient exceeded (induced losses)",
            "Weak formation after casing shoe (low FG)",
        ],
        prevention=[
            "Keep ECD below fracture gradient: control ROP, mud weight, rheology",
            "Use proper hole cleaning without high surge pressures",
            "Run LCM treatments preventively in known loss zones",
            "Plan casing points to isolate loss zones early",
            "Maintain continuous fill of hole while tripping",
        ],
        remedies=[
            "1) Stop drilling, pick up off bottom, reduce pump rate, monitor level",
            "2) For seepage: continue with LCM sweeps (mica, nut plug, fibers)",
            "3) For partial loss: spot high-vis / LCM pill; pump LCM at low rate",
            "4) For severe loss: spot gunk pill (bentonite + diesel) or thixotropic plug",
            "5) If returns not regained: cement plug / chemical (cross-linked) plug",
            "6) Drill ahead with controlled parameters; keep mud system treated",
            "7) If total loss to thief zone: consider blind drilling with water/salt water if safe",
        ],
        related_procedures=["LCM Pills", "Gunk Pill Pumping", "Cement Plug (Loss Zone)", "Lost Returns Contingency"],
        library_refs=["263", "364", "493", "363"],
    ),
    DrillingProblem(
        code="LC-02", category="Lost Circulation", name="Gunk Pill (Bentonite-Diesel) Spotting",
        severity="Medium",
        symptoms=[
            "Severe/total loss zone where conventional LCM fails",
            "No returns at surface while pumping",
        ],
        causes=["High-permeability or fractured thief zones"],
        prevention=["Pre-mix gunk materials and maintain diesel supply for contingency"],
        remedies=[
            "1) Mix gunk (bentonite + diesel) with seawater ahead of spacer",
            "2) Pump spacer, gunk pill, then displacement fluid; displace to bit",
            "3) Pull above the zone and wait (gunk sets like a plug)",
            "4) Tag top of gunk, drill slowly with controlled parameters",
            "5) If not effective, repeat with higher concentration or cement plug",
        ],
        related_procedures=["Gunk Pill Pumping Procedure", "Lost Circulation Control"],
        library_refs=["363"],
    ),

    # ======================================================= WELL CONTROL
    DrillingProblem(
        code="WC-01", category="Well Control", name="Kick / Influx",
        severity="Critical",
        symptoms=[
            "Flow at the flow-line with pumps off (primary indicator)",
            "Pit volume gain",
            "Flow increase while drilling / circulating (flow meter increase)",
            "Connection gas / trip gas (background)",
            "Drilling break (ROP increase into higher-pressure zone)",
            "Pump pressure decrease and pump stroke increase (lighter fluid in hole)",
        ],
        causes=[
            "Mud weight below formation pore pressure (insufficient overbalance)",
            "Swabbing while tripping (fast POOH, plugged nozzles, balled bit)",
            "Failure to keep hole full while tripping",
            "Lost circulation → mud level drop → underbalance",
            "Abnormal pressure unexpected (no seismic / offset data)",
        ],
        prevention=[
            "Maintain design mud weight + safe overbalance margin",
            "Trip procedures: fill hole, controlled POOH speed, flow checks",
            "Keep trip tank calibrated and monitored",
            "Drill breaks: stop and flow-check immediately",
            "Well-control drills & BOP tests per company policy",
            "Monitor connection gas trends; treat mud as required",
        ],
        remedies=[
            "1) SHUT IN: follow the shut-in procedure (close BOP, shut down pump)",
            "2) Record SIDPP / SICP and pit gain",
            "3) Verify kick: flow check, trip tank, pit volume",
            "4) Use Driller's Method: circulate kick out at old MW, then weight up",
            "5) Or Wait-and-Weight: weight up and circulate in one circulation",
            "6) Circulate at slow pump rate (kill rate); hold BHP constant",
            "7) After kill: verify with flow check; condition mud",
        ],
        related_procedures=["Driller's Method", "Wait & Weight Method", "Well Control Drill", "BOP Test"],
        library_refs=["263", "364", "493", "357"],
    ),
    DrillingProblem(
        code="WC-02", category="Well Control", name="Shallow Gas",
        severity="Critical",
        symptoms=[
            "Gas cut mud / connection gas at shallow depths",
            "Pit gain / flow increase at shallow depth",
            "Possible broaching around conductor",
        ],
        causes=[
            "Shallow gas sands with abnormal pressure",
            "Low mud weight / no BOP stack installed (top-hole drilling)",
            "Gas kick undetected due to no returns / floating drilling",
        ],
        prevention=[
            "Pre-spud hazard assessment & shallow-gas contingency plan",
            "Gas detection equipment and divertor system tested",
            "BOP stack (or diverter) installed before drilling shallow gas zones",
            "Sea water / natural mud; low ROP near gas sands; watch for drilling breaks",
            "Vessel/rig positioned to move off location if required (floating)",
        ],
        remedies=[
            "1) Divert: open diverter line downwind, keep well flowing to divertor",
            "2) Alert crew; initiate emergency response (muster, shut down ignition sources)",
            "3) If BOP installed: shut in if safe and well can be controlled",
            "4) Weight up and circulate out as per well-control procedure",
            "5) If broaching: prepare to abandon location per emergency plan",
        ],
        related_procedures=["Shallow Gas Procedure", "Well Control Drill", "Divertor Operation"],
        library_refs=["364"],
    ),
    DrillingProblem(
        code="WC-03", category="Well Control", name="Blowout (Surface / Underground)",
        severity="Critical",
        symptoms=[
            "Uncontrolled flow of formation fluids to surface / into another formation",
            "Failure of BOP / wellhead / casing to contain the well",
            "Fire or gas cloud at surface in extreme cases",
        ],
        causes=[
            "Kick not detected or not controlled in time",
            "BOP equipment failure / not tested",
            "Casing / wellhead integrity failure",
            "Underground blowout via loss zone",
        ],
        prevention=[
            "Robust well-control barrier policy: two verified barriers",
            "Regular BOP tests, drift tests, casing integrity tests",
            "Kick detection instrumentation calibrated & manned",
            "Drill well-control scenarios; keep crews trained",
        ],
        remedies=[
            "1) Emergency response: muster, shut down ignition sources, activate alarms",
            "2) Attempt to close BOP (rams/annular) as designed",
            "3) If surface blowout: prepare relief well plan & specialist intervention",
            "4) If underground: bullhead or dynamic kill via relief well",
            "5) Preserve evidence & records for investigation",
        ],
        related_procedures=["Well Control Drill", "Emergency Response", "Relief Well Planning"],
        library_refs=["263", "364"],
    ),

    # ====================================================== HOLE STABILITY
    DrillingProblem(
        code="HS-01", category="Hole Stability", name="Shale Swelling / Instability",
        severity="High",
        symptoms=[
            "Cavings at shaker (soft, angular or 'splintery' cavings)",
            "Hole enlargement (caliper shows washouts)",
            "Bridges and fill on trips",
            "Stuck pipe and fishing difficulty",
            "Hole-cleaning problems; torque/drag increase",
            "High fluid-maintenance cost",
        ],
        causes=[
            "Water adsorption by reactive clays (hydration)",
            "Chemical incompatibility of mud with shale (osmotic effects)",
            "Insufficient mud weight to support wellbore (stress failure)",
            "Poor filter cake / fluid loss control",
        ],
        prevention=[
            "Use inhibitive mud systems (KCl/Polymer, PHPA, OBM/SBM in reactive sections)",
            "Maintain adequate mud weight for stress support",
            "Control fluid loss (API/HPHT) to reduce water invasion",
            "Minimize exposure time; drill and case reactive sections quickly",
            "Sealants / asphaltic additives for micro-fractures",
        ],
        remedies=[
            "1) Increase mud inhibition (KCl, polymer, salt) as applicable",
            "2) Raise mud weight in small steps if hole closure indicated",
            "3) Circulate and ream; make wiper trips to clean hole",
            "4) Spot inhibitive/salt-saturated pill across problem interval",
            "5) If severe: consider changeover to OBM/SBM for the section",
        ],
        related_procedures=["Hole Cleaning", "Mud Program Design", "Wiper Trips"],
        library_refs=["295", "363", "493"],
    ),
    DrillingProblem(
        code="HS-02", category="Hole Stability", name="Hole Collapse / Caving",
        severity="High",
        symptoms=[
            "Large cavings at surface; hole fill after trips",
            "Circulation pressure increase (pack-off)",
            "Torque/drag increase; tight hole",
            "Lost circulation followed by gains (stress-release)",
        ],
        causes=[
            "Rock stress exceeds rock strength (insufficient MW)",
            "Tectonic / in-situ stresses (faults, dipping beds)",
            "Reactive shales weakening the rock",
            "Swab/surge pressure cycling",
        ],
        prevention=[
            "Maintain MW ≥ minimum required for wellbore stability (not just pore pressure)",
            "Avoid rapid pipe movement (surge/swab)",
            "Use low-ECD systems; keep hole clean",
            "Case off unstable intervals as soon as practical",
        ],
        remedies=[
            "1) Increase mud weight gradually to stabilize the wellbore",
            "2) Circulate bottoms-up; inspect cavings to diagnose mechanism",
            "3) Ream and condition hole before tripping",
            "4) If collapse blocks hole: work pipe, pump high-vis sweeps",
            "5) Consider setting casing earlier if stability cannot be achieved",
        ],
        related_procedures=["Hole Cleaning", "Mud Weight Management"],
        library_refs=["295", "363"],
    ),
    DrillingProblem(
        code="HS-03", category="Hole Stability", name="Bit Balling / Mud Ring",
        severity="Medium",
        symptoms=[
            "ROP decreases while parameters constant",
            "Pump pressure increases (annulus restriction)",
            "Cuttings not reaching shaker (bit balled, mud ring around BHA)",
            "High solids in mud; poor cuttings shape (rounded/balled)",
        ],
        causes=[
            "Sticky/gumbo shales adhering to bit & BHA",
            "Insufficient hydraulics (low jet velocity)",
            "Poor mud inhibition / high solids",
            "Inadequate hole cleaning in high-angle wells",
        ],
        prevention=[
            "Use anti-balling bit designs / PDC with adequate hydraulic power",
            "Maintain high bit HSI and nozzle velocity",
            "Inhibitive mud; keep low-gravity solids low",
            "Sweeps and wiper trips in gumbo intervals",
        ],
        remedies=[
            "1) Increase flow rate / improve hydraulics",
            "2) Pump high-vis pill and circulate bottoms-up",
            "3) Short trip / wiper trip to condition hole",
            "4) If mud ring: circulate, rotate and work pipe through the interval",
            "5) Change bit design if balling persists",
        ],
        related_procedures=["Hydraulics Design", "Hole Cleaning"],
        library_refs=["363", "246"],
    ),
    DrillingProblem(
        code="HS-04", category="Hole Stability", name="Deviation & Doglegs",
        severity="Medium",
        symptoms=[
            "Wellbore deviates from planned trajectory (surveys)",
            "Doglegs cause key seating, drag, casing wear",
            "Difficult directional control / high torque",
        ],
        causes=[
            "Bit/formation interaction (dip, hardness contrast)",
            "Insufficient stabilization / wrong BHA design",
            "Excessive WOB with low RPM in deviated hole",
            "Poor directional supervision",
        ],
        prevention=[
            "Design BHA (pendulum/packed) per formation tendencies",
            "Use MWD surveys frequently; follow directional plan",
            "Control WOB/RPM to manage build/drop tendencies",
            "Use RSS/motor with proper steering parameters",
        ],
        remedies=[
            "1) Re-plan trajectory; set correction runs (sidetrack if necessary)",
            "2) Adjust BHA (add/remove stabilizers) to control tendency",
            "3) Reduce DLS in future sections to avoid key seats",
            "4) Monitor casing wear in doglegs (wear models, calipers)",
        ],
        related_procedures=["Directional Planning", "Survey Procedures", "BHA Design"],
        library_refs=["322"],
    ),
    DrillingProblem(
        code="HS-05", category="Hole Stability", name="Gauge Problems (7 Gauge Checks)",
        severity="Medium",
        symptoms=[
            "Ring gauge doesn't pass / tight gauge while tripping",
            "Drag on connections; inability to rotate through tight spots",
            "Under-gauge hole from swelling formations",
        ],
        causes=[
            "Shale swelling, salt creep, under-gauge hole",
            "Worn bit gauge, poor stabilizer condition",
            "Casing collapse / deformation",
        ],
        prevention=[
            "Run gauge protection / gauge ring checks routinely",
            "Maintain bit gauge & stabilizer OD within tolerance",
            "Use inhibitive mud to prevent swelling",
        ],
        remedies=[
            "1) Ream tight intervals; work pipe",
            "2) Check bit/stabilizers for gauge wear on trips",
            "3) If salt creep: increase MW / use salt-saturated mud",
            "4) Consider under-reamer in known problem sections",
        ],
        related_procedures=["Gauge Ring Procedure", "Tripping Procedures"],
        library_refs=["246"],
    ),

    # ============================================================ FISHING
    DrillingProblem(
        code="FI-01", category="Fishing", name="Fishing Operations (General)",
        severity="High",
        symptoms=[
            "Fish in hole: parted string, junk, tools, stuck fish",
            "No personnel in exposed position while pulling/jarring",
        ],
        causes=[
            "Twist-off, part, dropped tools, junk, stuck pipe back-off",
        ],
        prevention=[
            "Inspect drill string (DP/DC) regularly; manage fatigue & corrosion",
            "Torque management within connection limits",
            "Catch junk early with magnets/baskets",
            "Maintain fishing kit and trained supervisor",
        ],
        remedies=[
            "1) SAFETY first: clear drill floor, inspect derrick before jarring",
            "2) Standard fishing assembly: overshot / bumper sub / DC / jar / accelerator / HWDP",
            "3) Use spiral grapple in preference to basket grapple; run extension",
            "4) If overshot fails to locate fish in washed-out hole: bent sub or wall hook",
            "5) Circulate clean and spot viscous pill before POOH if twist-off",
            "6) Mill / washover if needed; internal cutters for washover string",
            "7) If fish not recovered: cement plug & sidetrack",
        ],
        related_procedures=["Fishing Assembly", "Back-Off & Free Point", "Milling", "Washover"],
        library_refs=["363", "263"],
    ),
    DrillingProblem(
        code="FI-02", category="Fishing", name="Free Point & Back-Off",
        severity="High",
        symptoms=[
            "Stuck pipe where the free point must be determined before cutting",
            "Twist-off / part leaving fish",
        ],
        causes=["Stuck pipe (differential/mechanical) — see SP-01..03"],
        prevention=["Jars in BHA; free-point indicator available"],
        remedies=[
            "1) Run free-point indicator (wireline) to locate stuck point",
            "2) Apply right-hand torque (string shot) at the free point",
            "3) Back off at the connection; POOH free string",
            "4) Prepare fishing assembly for the fish",
            "5) Keep detailed tally and drawings of fish",
        ],
        related_procedures=["Free Point & Back-off", "Fishing"],
        library_refs=["263", "264", "265"],
    ),
    DrillingProblem(
        code="FI-03", category="Fishing", name="Junk in Hole",
        severity="High",
        symptoms=[
            "Metal/foreign debris on bottom (cones, slips, tools)",
            "Impossible to drill ahead; bit damage",
        ],
        causes=[
            "Bit cone loss, dropped tools, debris from milling",
        ],
        prevention=[
            "Inspect bits & tools; catch cones early (magnets, baskets)",
            "Keep drill floor clean; controlled tool handling",
        ],
        remedies=[
            "1) Run junk basket / boot basket to catch small debris",
            "2) Run junk mill to grind down junk to small pieces",
            "3) Use magnet for magnetic junk",
            "4) If large junk: fish with overshot/washover",
            "5) If not recoverable: cement & sidetrack",
        ],
        related_procedures=["Junk Mill", "Fishing", "Sidetrack"],
        library_refs=["363", "364"],
    ),

    # ============================================================== CEMENT
    DrillingProblem(
        code="CM-01", category="Cementing", name="Cementing Problems (Lost Returns / Channeling / No Bump)",
        severity="High",
        symptoms=[
            "Loss of returns during cement job",
            "No pressure bump at plug (plug not landed)",
            "Cement channels / poor bond (CBL/VDL shows bad bond)",
            "Gas migration / flow after cement",
            "Cement not setting (wrong additives/water)",
        ],
        causes=[
            "ECD exceeds fracture gradient during displacement",
            "Insufficient cement volume / wrong slurry design",
            "Centralization poor → channeling",
            "Mud not conditioned / spacer not effective",
            "Contamination of slurry (mixing water, mud)",
        ],
        prevention=[
            "Design slurry & displacement for the section (density, fluid loss, free water)",
            "Condition mud & hole before job; run spacer (turbulent flow)",
            "Centralize casing (standoff ≥ 70%)",
            "Use top & bottom plugs; proper wiper; monitor returns",
            "Hang-off / job procedures per program",
        ],
        remedies=[
            "1) If lost returns: reduce rate, consider low-density (foam/lightweight) slurry next time",
            "2) If no bump: circulate, wait on cement, log (CBL/VDL) to evaluate",
            "3) If channeling: squeeze cement (remedial) through perforations / scab liner",
            "4) If gas migration: verify annulus pressure, bleed as per plan, consider annular packing",
            "5) If not set: WOC longer, evaluate with logs, re-cement if needed",
        ],
        related_procedures=["Primary Cementing", "Cement Squeeze", "CBL/VDL Evaluation"],
        library_refs=["310", "263"],
    ),

    # ========================================================== EQUIPMENT
    DrillingProblem(
        code="EQ-01", category="Equipment", name="Rig Equipment / Pump Problems",
        severity="Medium",
        symptoms=[
            "Mud pump failure / pressure fluctuations",
            "Drawworks / top drive / iron roughneck breakdown",
            "Compressor / generator failure",
            "Operational downtime (NPT)",
        ],
        causes=[
            "Maintenance gaps, wear, misuse, spare parts shortage",
        ],
        prevention=[
            "Preventive maintenance program (PM) per OEM schedule",
            "Spare parts & critical spares on location",
            "Operator training & daily inspection checklists",
            "Redundancy: backup pumps, generators",
        ],
        remedies=[
            "1) Isolate and repair per OEM procedure",
            "2) Changeover to standby unit (pump/generator)",
            "3) If long downtime: review time breakdown & inform planning",
            "4) Root-cause analysis & report",
        ],
        related_procedures=["Equipment Maintenance", "Time Breakdown"],
        library_refs=["462"],
    ),

    # ======================================================= MUD PROBLEMS
    DrillingProblem(
        code="MU-01", category="Mud & Contamination", name="Mud Contamination",
        severity="Medium",
        symptoms=[
            "Rheology changes (viscosity up/down)",
            "Fluid loss increase; filter cake thick",
            "pH drop; hardness (Ca/Mg) increase",
            "Gas-cut mud; H2S/CO2 contamination",
            "Emulsion / oil contamination",
        ],
        causes=[
            "Evaporite salts (NaCl, KCl, CaCl2, anhydrite)",
            "Water flows (mixed salts)",
            "Acid gases (CO2, H2S)",
            "Cement contamination from cement job",
            "Hydrocarbons (oil, condensate)",
            "Temperature degradation of products",
            "Drilled solids accumulation",
        ],
        prevention=[
            "Treat mud system pre-emptively before drilling evaporites",
            "Monitor chemical analysis (hardness, chloride, pH) daily",
            "Use scavengers (H2S) & buffers as required",
            "Maintain solids-control equipment efficiency",
        ],
        remedies=[
            "1) Identify contaminant (test: hardness, chloride, pH, gas)",
            "2) Ca: precipitate with soda ash/NaHCO3",
            "3) Cl: tolerate or convert to salt-saturated system",
            "4) CO2/H2S: raise pH, use caustic soda + scavengers (zinc carbonate)",
            "5) Cement: treat with sodium bicarbonate",
            "6) Oil: emulsify with surfactants or dilute",
            "7) Increase dilution / solids control as required",
        ],
        related_procedures=["Mud Testing", "Mud Program Design"],
        library_refs=["295", "493"],
    ),
    DrillingProblem(
        code="MU-02", category="Mud & Contamination", name="Hole Cleaning Problems",
        severity="High",
        symptoms=[
            "Cuttings not reaching surface in expected time (lag)",
            "Fill on bottom; pack-offs; torque/drag increase",
            "High cuttings load in annulus (ECD increase)",
            "In high-angle wells: cuttings bed on low side",
        ],
        causes=[
            "Insufficient annular velocity",
            "Poor mud rheology (low YP / gels)",
            "High-angle / horizontal wellbore (cuttings beds)",
            "ROP too high for the hole cleaning capability",
        ],
        prevention=[
            "Design hydraulics: annular velocity ≥ critical velocity",
            "Maintain adequate YP & low-shear rheology",
            "Sweeps (high-vis, low-vis) & wiper trips per procedure",
            "Rotate & reciprocate while circulating in high-angle wells",
            "Use hole-cleaning models (ECD vs flow rate)",
        ],
        remedies=[
            "1) Circulate bottoms-up with rotation/reciprocation",
            "2) Pump high-vis sweeps; observe cuttings at shaker",
            "3) Reduce ROP until hole is clean",
            "4) Make wiper trips (short trips) to check fill",
            "5) Increase flow rate / improve rheology as per plan",
        ],
        related_procedures=["Hole Cleaning Procedure", "TD Hole Cleaning", "Hydraulics"],
        library_refs=["363", "364"],
    ),

    # ==================================================== DRILLING PRACTICE
    DrillingProblem(
        code="DP-01", category="Drilling Practice", name="Washout / Twist-off",
        severity="High",
        symptoms=[
            "Pump pressure sudden drop with no change in flow",
            "ROP drop; torque changes",
            "String washout → twist-off (fish)",
        ],
        causes=[
            "Pipe fatigue, corrosion, erosion (jetting, LCM)",
            "Over-torque / overpull",
            "Poor handling (clamps, slips) damage",
        ],
        prevention=[
            "Inspect & tally drill pipe; rotate pipe in slips; manage corrosion",
            "Torque management; avoid overpull",
            "Drift/OD inspection on regular basis",
        ],
        remedies=[
            "1) If washout suspected: stop, verify with pressure/flow check",
            "2) POOH and inspect string; replace damaged joints",
            "3) If twist-off: fishing operation (see FI-01)",
        ],
        related_procedures=["Fishing", "Drill String Inspection"],
        library_refs=["263", "363"],
    ),
    DrillingProblem(
        code="DP-02", category="Drilling Practice", name="Stick-Slip / Torsional Vibration",
        severity="Medium",
        symptoms=[
            "Surface torque oscillations (stick-slip)",
            "Downhole vibrations (shock tools data), BHA damage",
            "Poor ROP; bit damage; MWD failures",
        ],
        causes=[
            "High WOB, low RPM, bit/formation interaction",
            "Long BHA, poor damping, friction",
        ],
        prevention=[
            "Use vibration modeling / anti-stall tools",
            "Optimize WOB/RPM operating window",
            "Use PDC bits with appropriate blade/backrake design",
        ],
        remedies=[
            "1) Adjust RPM/WOB (usually increase RPM) to exit stick-slip",
            "2) Use downhole vibration dampener / torsional oscillator",
            "3) Change drilling parameters or bit design if persistent",
        ],
        related_procedures=["Drilling Parameters Optimization"],
        library_refs=["364"],
    ),
]

# ============================================================================
# DATABASE
# ============================================================================

class ProblemDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DEFAULT_DB
        APP_DIR.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._seed_if_empty()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS problems (
                code TEXT PRIMARY KEY,
                category TEXT,
                name TEXT,
                severity TEXT,
                symptoms TEXT,
                causes TEXT,
                prevention TEXT,
                remedies TEXT,
                related_procedures TEXT,
                library_refs TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_problems_cat ON problems(category);
        """)
        self.conn.commit()

    def _seed_if_empty(self):
        cur = self.conn.execute("SELECT COUNT(*) AS c FROM problems")
        if cur.fetchone()["c"] == 0:
            for p in PROBLEMS:
                self.conn.execute(
                    "INSERT INTO problems (code, category, name, severity, "
                    "symptoms, causes, prevention, remedies, "
                    "related_procedures, library_refs) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (p.code, p.category, p.name, p.severity,
                     json.dumps(p.symptoms), json.dumps(p.causes),
                     json.dumps(p.prevention), json.dumps(p.remedies),
                     json.dumps(p.related_procedures),
                     json.dumps(p.library_refs)))
            self.conn.commit()

    def close(self):
        self.conn.close()

    def all(self) -> List[DrillingProblem]:
        rows = self.conn.execute("SELECT * FROM problems ORDER BY "
                                 "CASE severity WHEN 'Critical' THEN 0 "
                                 "WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 "
                                 "ELSE 3 END, code").fetchall()
        return [self._row(r) for r in rows]

    def categories(self) -> List[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT category FROM problems ORDER BY category").fetchall()
        return [r["category"] for r in rows]

    def search(self, query: str) -> List[DrillingProblem]:
        q = query.lower()
        out = []
        for p in self.all():
            blob = " ".join([p.name, p.category] + p.symptoms + p.causes +
                            p.prevention + p.remedies).lower()
            if q in blob:
                out.append(p)
        return out

    def by_code(self, code: str) -> Optional[DrillingProblem]:
        r = self.conn.execute("SELECT * FROM problems WHERE code=?",
                              (code,)).fetchone()
        return self._row(r) if r else None

    @staticmethod
    def _row(r) -> DrillingProblem:
        def load(s):
            try:
                return json.loads(s or "[]")
            except Exception:
                return []
        return DrillingProblem(
            code=r["code"], category=r["category"], name=r["name"],
            severity=r["severity"], symptoms=load(r["symptoms"]),
            causes=load(r["causes"]), prevention=load(r["prevention"]),
            remedies=load(r["remedies"]),
            related_procedures=load(r["related_procedures"]),
            library_refs=load(r["library_refs"]))


# ============================================================================
# MARKDOWN SECTION for wizard output
# ============================================================================

def build_problems_markdown(problems: List[DrillingProblem],
                            operator: str = "") -> str:
    """Build a 'DRILLING PROBLEM PREVENTION & RESPONSE' section (markdown)."""
    lines = ["## DRILLING PROBLEM PREVENTION & RESPONSE PLAN", ""]
    if operator:
        lines.append(f"**Operator:** {operator}")
        lines.append("")
    lines.append("The following drilling problems are identified for this "
                 "operation together with prevention measures and response "
                 "procedures. All personnel shall be familiar with the "
                 "symptoms and the first response for each problem.")
    lines.append("")
    for p in problems:
        lines.append(f"### {p.code} — {p.name} ({p.severity} Risk)")
        lines.append("")
        lines.append(f"**Category:** {p.category}")
        lines.append("")
        lines.append("**Symptoms (warning signs):**")
        lines.append("")
        for s in p.symptoms:
            lines.append(f"- {s}")
        lines.append("")
        lines.append("**Causes:**")
        lines.append("")
        for c in p.causes:
            lines.append(f"- {c}")
        lines.append("")
        lines.append("**Prevention:**")
        lines.append("")
        for pr in p.prevention:
            lines.append(f"- {pr}")
        lines.append("")
        lines.append("**Response (in order):**")
        lines.append("")
        for i, r in enumerate(p.remedies, 1):
            lines.append(f"{i}. {r}")
        lines.append("")
        if p.related_procedures:
            lines.append("**Related procedures:** " +
                         ", ".join(p.related_procedures))
            lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    db = ProblemDatabase()
    probs = db.all()
    print(f"problems in DB: {len(probs)}")
    for c in db.categories():
        n = sum(1 for p in probs if p.category == c)
        print(f"  {c}: {n}")
    db.close()
