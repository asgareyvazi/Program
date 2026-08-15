# ============================================================================
# OFFSHORE / RE-ENTRY / WORKOVER WIZARD TEMPLATES
# File: wizard_offshore.py
# New templates modeled on the 25 offshore documents added to the library
# (Salman, Balal, Dorood, Foroozan, Siri fields — re-entry & sidetrack,
# workover with ESP change, drilling programs with full hydraulics).
# All templates are GENERAL: no well/company/reservoir names.
# ============================================================================

from wizard_engine import TemplateDef, InputSpec

# ----------------------------------------------------------------------------
# RE-ENTRY / SIDETRACK PROGRAM
# ----------------------------------------------------------------------------

REENTRY_PROGRAM_MD = r"""
# RE-ENTRY & SIDETRACK PROGRAM — {{well_name}}

**Field:** {{field_name}} | **Operator:** {{operator}} | **Rig:** {{rig_name}}
**Document No.:** {{document_number}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Re-enter well **{{well_name}}** in the {{field_name}} field and perform sidetrack /
re-entry operations as described in this program. The main objective is to
{{objective}}.

**Well Status:** {{well_status}}
**RKB-MSL:** {{rkb_msl}} m | **Total Depth (MD):** {{total_depth_md}} m
**Window Depth:** {{window_depth}} m (in {{window_casing}} casing)

## 2. WELL INFORMATION

| Item | Value |
|---|---|
| Well Name | {{well_name}} |
| Field | {{field_name}} |
| Well Type | {{well_type}} |
| Type of Operation | {{operation_type}} |
| Rig Name / Type | {{rig_name}} / {{rig_type}} |
| Surface Location E / N | {{loc_e}} / {{loc_n}} |
| RKB-MSL | {{rkb_msl}} m |
| Reservoir | {{reservoir}} |
| Datum Depth | {{datum_depth}} m TVD ss |
| Datum Pressure | {{datum_pressure}} psi |
| H2S | {{h2s}} |

## 3. EXISTING WELL ARCHITECTURE

{{well_architecture}}

## 4. WELL SKETCH BEFORE RE-ENTRY

{{sketch_before}}

## 5. WELL SKETCH AFTER RE-ENTRY

{{sketch_after}}

## 6. RE-ENTRY OPERATION SEQUENCE

1. {{op1}}
2. {{op2}}
3. {{op3}}
4. {{op4}}
5. {{op5}}
6. {{op6}}
7. {{op7}}
8. {{op8}}
9. {{op9}}
10. {{op10}}

**Attention:**
- All depths are referred to RKB-MSL; correct with active rig measurement.
- H2S safety equipment and services must be ready at the rig.
- Enough LCM, weighting material and pipe-free agent must be available.

## 7. DIRECTIONAL DRILLING PROGRAM

{{directional_plan}}

- Kick-off point: {{kop_depth}} m MD
- Build-up rate: {{bur}} deg/30m
- Maximum inclination: {{max_inc}} deg
- Target: {{target}}

## 8. BHA & BITS

{{bha_plan}}

## 9. MUD PROGRAM

{{mud_plan}}

| Section | Mud Type | MW (pcf) | Notes |
|---|---|---|---|
| {{section1}} | {{mud_type1}} | {{mw1}} | |
| {{section2}} | {{mud_type2}} | {{mw2}} | |
| {{section3}} | {{mud_type3}} | {{mw3}} | |

## 10. HYDRAULICS RECOMMENDATION

| Parameter | Value |
|---|---|
| Nozzles | {{nozzles}} |
| TFA | {{tfa}} in² |
| Pump Pressure | {{pump_pressure}} psi |
| Flow Rate | {{flow_rate}} gpm |
| Bit HSI | {{bit_hsi}} |

## 11. CASING & LINER PROGRAM

{{casing_plan}}

## 12. COMPLETION

{{completion_plan}}

## 13. TIME BREAKDOWN OF OPERATION

Refer to the Time Breakdown table ({{time_days}} days estimated, see
"⏱️ Time & Evaluation" tab / CBS cost section).

## 14. EQUIPMENT & MATERIAL REQUIREMENTS

{{requirements}}

## 15. CONTACT LIST

| Role | Company | Name | Phone |
|---|---|---|---|
| Drilling Engineer | {{operator}} | | |
| Operations | {{contractor}} | | |

## 16. HSE & EMERGENCY

- Hold pre-job safety meetings.
- All personnel must be H2S certified when H2S is present.
- PTW (Permit to Work) required for all simultaneous operations.
- Emergency response plan & muster points to be reviewed before start.

## APPROVAL

| Role | Name | Date | Signature |
|---|---|---|---|
| Prepared by | {{prepared_by}} | | |
| Reviewed by | {{reviewed_by}} | | |
| Approved by | {{approved_by}} | | |
"""

REENTRY_INPUTS = [
    # -- 1. General
    InputSpec("well_name", "Well Name", "text", placeholder="e.g. WELL-01", group="1. General"),
    InputSpec("field_name", "Field", "text", placeholder="e.g. Offshore Field", group="1. General"),
    InputSpec("operator", "Operator", "text", placeholder="e.g. Operator Name", group="1. General"),
    InputSpec("contractor", "Contractor", "text", placeholder="e.g. Service Company", group="1. General"),
    InputSpec("rig_name", "Rig Name", "text", placeholder="e.g. RIG-100", group="1. General"),
    InputSpec("rig_type", "Rig Type", "combo", options=["Jack-up", "Semi-submersible", "Drillship", "Land Rig"], group="1. General"),
    InputSpec("well_type", "Well Type", "combo", options=["Oil Well", "Gas Well", "Water Disposal", "Exploration"], group="1. General"),
    InputSpec("operation_type", "Operation Type", "combo", options=["Re-Entry", "Sidetrack", "Workover", "Drilling"], group="1. General"),
    InputSpec("well_status", "Well Status", "combo", options=["Shut-in", "Producing", "Suspended", "Abandoned"], group="1. General"),
    InputSpec("loc_e", "Surface Location E", "text", group="1. General"),
    InputSpec("loc_n", "Surface Location N", "text", group="1. General"),
    InputSpec("rkb_msl", "RKB-MSL", "number", unit="m", group="1. General"),
    InputSpec("document_number", "Document No.", "text", group="1. General"),
    # -- 2. Reservoir
    InputSpec("reservoir", "Reservoir", "text", placeholder="e.g. Main reservoir", group="2. Reservoir"),
    InputSpec("datum_depth", "Datum Depth", "number", unit="m TVD ss", group="2. Reservoir"),
    InputSpec("datum_pressure", "Datum Pressure", "number", unit="psi", group="2. Reservoir"),
    InputSpec("h2s", "H2S", "text", placeholder="e.g. 1.1 mole %", group="2. Reservoir"),
    # -- 3. Objective & history
    InputSpec("objective", "Main Objective", "textarea", placeholder="e.g. sidetrack to bypass collapsed liner", group="3. Objective"),
    InputSpec("well_architecture", "Existing Well Architecture", "textarea", placeholder="e.g. 36\" conductor @168m, 20\" csg @308m, 13-3/8\" @1076m, 9-5/8\" @2021m", group="3. Objective"),
    InputSpec("drilling_history", "Drilling / Workover History", "textarea", group="3. Objective"),
    # -- 4. Sidetrack / directional
    InputSpec("window_depth", "Window Depth", "number", unit="m", group="4. Sidetrack"),
    InputSpec("window_casing", "Window Casing", "text", placeholder="e.g. 9-5/8\"", group="4. Sidetrack"),
    InputSpec("kop_depth", "KOP Depth", "number", unit="m MD", group="4. Sidetrack"),
    InputSpec("bur", "Build-up Rate", "number", unit="deg/30m", group="4. Sidetrack"),
    InputSpec("max_inc", "Max Inclination", "number", unit="deg", group="4. Sidetrack"),
    InputSpec("target", "Target", "text", group="4. Sidetrack"),
    InputSpec("total_depth_md", "Total Depth (MD)", "number", unit="m", group="4. Sidetrack"),
    InputSpec("directional_plan", "Directional Plan", "textarea", group="4. Sidetrack"),
    # -- 5. Engineering
    InputSpec("bha_plan", "BHA & Bits", "textarea", placeholder="e.g. 8-1/2\" PDC bit + motor + MWD/GR/ROP", group="5. Engineering"),
    InputSpec("mud_plan", "Mud Plan", "textarea", group="5. Engineering"),
    InputSpec("section1", "Hole Section 1", "text", group="5. Engineering"),
    InputSpec("mud_type1", "Mud Type 1", "text", group="5. Engineering"),
    InputSpec("mw1", "MW 1", "number", unit="pcf", group="5. Engineering"),
    InputSpec("section2", "Hole Section 2", "text", group="5. Engineering"),
    InputSpec("mud_type2", "Mud Type 2", "text", group="5. Engineering"),
    InputSpec("mw2", "MW 2", "number", unit="pcf", group="5. Engineering"),
    InputSpec("section3", "Hole Section 3", "text", group="5. Engineering"),
    InputSpec("mud_type3", "Mud Type 3", "text", group="5. Engineering"),
    InputSpec("mw3", "MW 3", "number", unit="pcf", group="5. Engineering"),
    InputSpec("nozzles", "Nozzles", "text", placeholder="e.g. 6 x (10/32\")", group="5. Engineering"),
    InputSpec("tfa", "TFA", "number", unit="in²", group="5. Engineering"),
    InputSpec("pump_pressure", "Pump Pressure", "number", unit="psi", group="5. Engineering"),
    InputSpec("flow_rate", "Flow Rate", "number", unit="gpm", group="5. Engineering"),
    InputSpec("bit_hsi", "Bit HSI", "number", group="5. Engineering"),
    InputSpec("casing_plan", "Casing & Liner Program", "textarea", group="5. Engineering"),
    InputSpec("completion_plan", "Completion Plan", "textarea", group="5. Engineering"),
    # -- 6. Operations
    InputSpec("op1", "Operation Step 1", "text", group="6. Operation Sequence"),
    InputSpec("op2", "Operation Step 2", "text", group="6. Operation Sequence"),
    InputSpec("op3", "Operation Step 3", "text", group="6. Operation Sequence"),
    InputSpec("op4", "Operation Step 4", "text", group="6. Operation Sequence"),
    InputSpec("op5", "Operation Step 5", "text", group="6. Operation Sequence"),
    InputSpec("op6", "Operation Step 6", "text", group="6. Operation Sequence"),
    InputSpec("op7", "Operation Step 7", "text", group="6. Operation Sequence"),
    InputSpec("op8", "Operation Step 8", "text", group="6. Operation Sequence"),
    InputSpec("op9", "Operation Step 9", "text", group="6. Operation Sequence"),
    InputSpec("op10", "Operation Step 10", "text", group="6. Operation Sequence"),
    InputSpec("time_days", "Estimated Days", "number", unit="days", group="6. Operation Sequence"),
    # -- 7. Requirements & HSE
    InputSpec("requirements", "Equipment & Material Requirements", "textarea",
              placeholder="e.g. BHA & bits, scraper, whipstock, fishing tools, LCM, H2S eq.",
              group="7. Requirements & HSE"),
    InputSpec("sketch_before", "Well Sketch Before (text)", "textarea", group="7. Requirements & HSE"),
    InputSpec("sketch_after", "Well Sketch After (text)", "textarea", group="7. Requirements & HSE"),
    InputSpec("hse_notes", "HSE Notes", "textarea", group="7. Requirements & HSE"),
]

REENTRY_TEMPLATE = TemplateDef(
    key="reentry_program",
    name="Re-Entry / Sidetrack Program",
    icon="🔄",
    kind="Program",
    description="Re-entry & sidetrack program (window in casing, directional "
                "sidetrack, completion) modeled on offshore re-entry programs "
                "(Salman / Balal / Dorood style).",
    inputs=REENTRY_INPUTS,
    markdown=REENTRY_PROGRAM_MD,
    meta={"category": "Programs", "new": True},
)

# ----------------------------------------------------------------------------
# OFFSHORE WORKOVER PROGRAM (ESP CHANGE / COMPLETION)
# ----------------------------------------------------------------------------

OFFSHORE_WORKOVER_MD = r"""
# WORKOVER PROGRAM — {{well_name}}

**Field:** {{field_name}} | **Operator:** {{operator}} | **Rig:** {{rig_name}}
**Document No.:** {{document_number}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. INTRODUCTION

This program covers the information and procedures required for the workover
operation on well **{{well_name}}** in the {{field_name}} field.

**Problem:** {{problem}}
**Main Objective:** {{objective}}

## 2. WELL INFORMATION

| Item | Value |
|---|---|
| Rig Name / Type | {{rig_name}} / {{rig_type}} |
| Well Name | {{well_name}} |
| Field | {{field_name}} |
| Well Type | {{well_type}} |
| Operation Type | {{operation_type}} |
| RKB-MSL | {{rkb_msl}} m |
| Well Status | {{well_status}} |
| Total Depth | {{total_depth}} m |
| PBTD | {{pbt_depth}} m |
| Perforation Interval | {{perforation_interval}} |

## 3. RESERVOIR DATA

| Item | Value |
|---|---|
| Reservoir | {{reservoir}} |
| Datum Depth | {{datum_depth}} m TVD ss |
| Datum Pressure | {{datum_pressure}} psi |
| Oil Gradient | {{oil_gradient}} |
| H2S | {{h2s}} |

## 4. WELL HISTORY

{{well_history}}

## 5. EXISTING COMPLETION (BEFORE WORKOVER)

{{completion_before}}

## 6. COMPLETION STRING AFTER WORKOVER

{{completion_after}}

## 7. WORKOVER OPERATION SEQUENCE

1. {{op1}}
2. {{op2}}
3. {{op3}}
4. {{op4}}
5. {{op5}}
6. {{op6}}
7. {{op7}}
8. {{op8}}
9. {{op9}}
10. {{op10}}

**Attention:**
- All depths referred to RKB-MSL (correct with active rig).
- H2S equipment & services ready (H2S present in reservoir).
- Any deviation from this program requires an amendment approved by {{operator}}.

## 8. KILL & WELL SECURING

{{kill_plan}}

## 9. COMPLETION / ESP RUNNING

{{completion_plan}}

## 10. TIME BREAKDOWN OF OPERATION

Estimated rig days: **{{time_days}} days** (see "⏱️ Time & Evaluation" tab).

## 11. EQUIPMENT & MATERIAL REQUIREMENTS

{{requirements}}

## 12. CONTACT LIST

| Role | Company | Name | Phone |
|---|---|---|---|
| Drilling Engineer | {{operator}} | | |
| Operations | {{contractor}} | | |

## 13. HSE & EMERGENCY

- Pre-job safety meetings before each major operation.
- H2S drills per company policy.
- PTW required for all simultaneous operations.
- Emergency response plan & muster points reviewed before start.

## APPROVAL

| Role | Name | Date | Signature |
|---|---|---|---|
| Prepared by | {{prepared_by}} | | |
| Reviewed by | {{reviewed_by}} | | |
| Approved by | {{approved_by}} | | |
"""

OFFSHORE_WORKOVER_INPUTS = [
    InputSpec("well_name", "Well Name", "text", placeholder="e.g. WELL-01P", group="1. General"),
    InputSpec("field_name", "Field", "text", placeholder="e.g. Offshore Field", group="1. General"),
    InputSpec("operator", "Operator", "text", placeholder="e.g. Operator Name", group="1. General"),
    InputSpec("contractor", "Contractor", "text", placeholder="e.g. Service Company", group="1. General"),
    InputSpec("rig_name", "Rig Name", "text", placeholder="e.g. RIG-200", group="1. General"),
    InputSpec("rig_type", "Rig Type", "combo", options=["Jack-up", "Semi-submersible", "Drillship", "Land Rig"], group="1. General"),
    InputSpec("well_type", "Well Type", "combo", options=["Oil Well", "Gas Well", "Water Disposal", "Exploration"], group="1. General"),
    InputSpec("operation_type", "Operation Type", "combo", options=["Workover", "Re-Entry", "ESP Change", "Completion"], group="1. General"),
    InputSpec("well_status", "Well Status", "combo", options=["Shut-in", "Producing", "Suspended"], group="1. General"),
    InputSpec("rkb_msl", "RKB-MSL", "number", unit="m", group="1. General"),
    InputSpec("total_depth", "Total Depth", "number", unit="m", group="1. General"),
    InputSpec("pbt_depth", "PBTD", "number", unit="m", group="1. General"),
    InputSpec("perforation_interval", "Perforation Interval", "text", group="1. General"),
    InputSpec("document_number", "Document No.", "text", group="1. General"),
    InputSpec("problem", "Problem", "textarea", placeholder="e.g. well shut-in to change ESP", group="2. Objective"),
    InputSpec("objective", "Main Objective", "textarea", placeholder="e.g. change ESP string and bring well back to production", group="2. Objective"),
    InputSpec("reservoir", "Reservoir", "text", group="3. Reservoir"),
    InputSpec("datum_depth", "Datum Depth", "number", unit="m TVD ss", group="3. Reservoir"),
    InputSpec("datum_pressure", "Datum Pressure", "number", unit="psi", group="3. Reservoir"),
    InputSpec("oil_gradient", "Oil Gradient", "number", group="3. Reservoir"),
    InputSpec("h2s", "H2S", "text", group="3. Reservoir"),
    InputSpec("well_history", "Well History", "textarea", group="4. History"),
    InputSpec("completion_before", "Completion Before Workover", "textarea", group="5. Completion"),
    InputSpec("completion_after", "Completion After Workover", "textarea", group="5. Completion"),
    InputSpec("kill_plan", "Kill & Well Securing Plan", "textarea", placeholder="e.g. kill with 72 pcf brine, N/D X-mas tree, N/U BOP & test", group="6. Operations"),
    InputSpec("completion_plan", "Completion / ESP Running Plan", "textarea", group="6. Operations"),
    InputSpec("op1", "Operation Step 1", "text", group="6. Operations"),
    InputSpec("op2", "Operation Step 2", "text", group="6. Operations"),
    InputSpec("op3", "Operation Step 3", "text", group="6. Operations"),
    InputSpec("op4", "Operation Step 4", "text", group="6. Operations"),
    InputSpec("op5", "Operation Step 5", "text", group="6. Operations"),
    InputSpec("op6", "Operation Step 6", "text", group="6. Operations"),
    InputSpec("op7", "Operation Step 7", "text", group="6. Operations"),
    InputSpec("op8", "Operation Step 8", "text", group="6. Operations"),
    InputSpec("op9", "Operation Step 9", "text", group="6. Operations"),
    InputSpec("op10", "Operation Step 10", "text", group="6. Operations"),
    InputSpec("time_days", "Estimated Days", "number", unit="days", group="6. Operations"),
    InputSpec("requirements", "Equipment & Material Requirements", "textarea",
              placeholder="e.g. ESP string, cable, packer, TRSV, slickline, CTU, acid",
              group="7. Requirements & HSE"),
]

OFFSHORE_WORKOVER_TEMPLATE = TemplateDef(
    key="offshore_workover_program",
    name="Offshore Workover Program (ESP/Completion)",
    icon="🏗️",
    kind="Program",
    description="Workover program (kill & secure, POOH completion, ESP change, "
                "run new completion) modeled on Balal / Foroozan workover "
                "programs.",
    inputs=OFFSHORE_WORKOVER_INPUTS,
    markdown=OFFSHORE_WORKOVER_MD,
    meta={"category": "Programs", "new": True},
)

# ----------------------------------------------------------------------------
# OFFSHORE DRILLING PROGRAM (with full hydraulics)
# ----------------------------------------------------------------------------

OFFSHORE_DRILLING_MD = r"""
# DRILLING PROGRAM — {{well_name}}

**Field:** {{field_name}} | **Operator:** {{operator}} | **Rig:** {{rig_name}}
**Document No.:** {{document_number}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. GENERAL INFORMATION

| Item | Value |
|---|---|
| Well Name | {{well_name}} |
| Field | {{field_name}} |
| Well Type | {{well_type}} |
| Rig Name / Type | {{rig_name}} / {{rig_type}} |
| RKB-MSL | {{rkb_msl}} m |
| Total Depth | {{total_depth}} m |
| Well Objective | {{well_objective}} |

## 2. WELL ARCHITECTURE

{{well_architecture}}

## 3. GEOLOGICAL & FORMATION TOPS

| Formation | MD Top (m) | TVD Top (m) | Notes |
|---|---|---|---|
| {{fm1}} | {{fm1_md}} | {{fm1_tvd}} | |
| {{fm2}} | {{fm2_md}} | {{fm2_tvd}} | |
| {{fm3}} | {{fm3_md}} | {{fm3_tvd}} | |

## 4. DIRECTIONAL PLAN

{{directional_plan}}

## 5. CASING PROGRAM

{{casing_plan}}

## 6. MUD PROGRAM

| Section | Mud Type | MW (pcf) | Notes |
|---|---|---|---|
| {{section1}} | {{mud_type1}} | {{mw1}} | |
| {{section2}} | {{mud_type2}} | {{mw2}} | |
| {{section3}} | {{mud_type3}} | {{mw3}} | |

## 7. BHA & DRILLING PARAMETERS

{{bha_plan}}

## 8. HYDRAULICS RECOMMENDATION

| Parameter | Value |
|---|---|
| Nozzles | {{nozzles}} |
| TFA | {{tfa}} in² |
| Pump Pressure | {{pump_pressure}} psi |
| Flow Rate | {{flow_rate}} gpm |
| Bit HSI | {{bit_hsi}} |
| System Pressure Loss | {{sys_pressure_loss}} psi |
| Bit Nozzle Pressure Drop | {{bit_pressure_drop}} psi |
| Nozzle Velocity | {{nozzle_velocity}} m/s |
| Jet Impact Force | {{jet_impact}} lbs |
| ECD | {{ecd}} pcf |
| Cutting Slip Velocity | {{chip_velocity}} m/min |

## 9. WELL CONTROL

{{well_control_plan}}

## 10. COMPLETION

{{completion_plan}}

## 11. TIME BREAKDOWN

Estimated duration: **{{time_days}} days** (see "⏱️ Time & Evaluation" tab).

## 12. EQUIPMENT & MATERIAL REQUIREMENTS

{{requirements}}

## 13. HSE & EMERGENCY

- Pre-job safety meetings before each major operation.
- H2S drills per company policy.
- PTW required for all simultaneous operations.
- Emergency response plan & muster points reviewed before start.

## APPROVAL

| Role | Name | Date | Signature |
|---|---|---|---|
| Prepared by | {{prepared_by}} | | |
| Reviewed by | {{reviewed_by}} | | |
| Approved by | {{approved_by}} | | |
"""

OFFSHORE_DRILLING_INPUTS = [
    InputSpec("well_name", "Well Name", "text", placeholder="e.g. WELL-25", group="1. General"),
    InputSpec("field_name", "Field", "text", placeholder="e.g. Offshore Field", group="1. General"),
    InputSpec("operator", "Operator", "text", placeholder="e.g. Operator Name", group="1. General"),
    InputSpec("contractor", "Contractor", "text", placeholder="e.g. Service Company", group="1. General"),
    InputSpec("rig_name", "Rig Name", "text", placeholder="e.g. RIG-300", group="1. General"),
    InputSpec("rig_type", "Rig Type", "combo", options=["Jack-up", "Semi-submersible", "Drillship", "Land Rig"], group="1. General"),
    InputSpec("well_type", "Well Type", "combo", options=["Oil Well", "Gas Well", "Water Disposal", "Exploration"], group="1. General"),
    InputSpec("rkb_msl", "RKB-MSL", "number", unit="m", group="1. General"),
    InputSpec("total_depth", "Total Depth", "number", unit="m", group="1. General"),
    InputSpec("well_objective", "Well Objective", "textarea", group="1. General"),
    InputSpec("document_number", "Document No.", "text", group="1. General"),
    InputSpec("well_architecture", "Well Architecture", "textarea", group="2. Architecture"),
    InputSpec("fm1", "Formation 1", "text", group="3. Geology"),
    InputSpec("fm1_md", "Formation 1 MD Top", "number", unit="m", group="3. Geology"),
    InputSpec("fm1_tvd", "Formation 1 TVD Top", "number", unit="m", group="3. Geology"),
    InputSpec("fm2", "Formation 2", "text", group="3. Geology"),
    InputSpec("fm2_md", "Formation 2 MD Top", "number", unit="m", group="3. Geology"),
    InputSpec("fm2_tvd", "Formation 2 TVD Top", "number", unit="m", group="3. Geology"),
    InputSpec("fm3", "Formation 3", "text", group="3. Geology"),
    InputSpec("fm3_md", "Formation 3 MD Top", "number", unit="m", group="3. Geology"),
    InputSpec("fm3_tvd", "Formation 3 TVD Top", "number", unit="m", group="3. Geology"),
    InputSpec("directional_plan", "Directional Plan", "textarea", group="4. Directional"),
    InputSpec("casing_plan", "Casing Program", "textarea", group="5. Casing"),
    InputSpec("section1", "Hole Section 1", "text", group="6. Mud"),
    InputSpec("mud_type1", "Mud Type 1", "text", group="6. Mud"),
    InputSpec("mw1", "MW 1", "number", unit="pcf", group="6. Mud"),
    InputSpec("section2", "Hole Section 2", "text", group="6. Mud"),
    InputSpec("mud_type2", "Mud Type 2", "text", group="6. Mud"),
    InputSpec("mw2", "MW 2", "number", unit="pcf", group="6. Mud"),
    InputSpec("section3", "Hole Section 3", "text", group="6. Mud"),
    InputSpec("mud_type3", "Mud Type 3", "text", group="6. Mud"),
    InputSpec("mw3", "MW 3", "number", unit="pcf", group="6. Mud"),
    InputSpec("bha_plan", "BHA & Drilling Parameters", "textarea", group="7. BHA"),
    InputSpec("nozzles", "Nozzles", "text", placeholder="e.g. 6 x (10/32\")", group="8. Hydraulics"),
    InputSpec("tfa", "TFA", "number", unit="in²", group="8. Hydraulics"),
    InputSpec("pump_pressure", "Pump Pressure", "number", unit="psi", group="8. Hydraulics"),
    InputSpec("flow_rate", "Flow Rate", "number", unit="gpm", group="8. Hydraulics"),
    InputSpec("bit_hsi", "Bit HSI", "number", group="8. Hydraulics"),
    InputSpec("sys_pressure_loss", "System Pressure Loss", "number", unit="psi", group="8. Hydraulics"),
    InputSpec("bit_pressure_drop", "Bit Nozzle Pressure Drop", "number", unit="psi", group="8. Hydraulics"),
    InputSpec("nozzle_velocity", "Nozzle Velocity", "number", unit="m/s", group="8. Hydraulics"),
    InputSpec("jet_impact", "Jet Impact Force", "number", unit="lbs", group="8. Hydraulics"),
    InputSpec("ecd", "ECD", "number", unit="pcf", group="8. Hydraulics"),
    InputSpec("chip_velocity", "Cutting Slip Velocity", "number", unit="m/min", group="8. Hydraulics"),
    InputSpec("well_control_plan", "Well Control Plan", "textarea", group="9. Well Control"),
    InputSpec("completion_plan", "Completion Plan", "textarea", group="10. Completion"),
    InputSpec("time_days", "Estimated Days", "number", unit="days", group="11. Time"),
    InputSpec("requirements", "Equipment & Material Requirements", "textarea", group="12. Requirements"),
]

OFFSHORE_DRILLING_TEMPLATE = TemplateDef(
    key="offshore_drilling_program",
    name="Offshore Drilling Program",
    icon="🛳️",
    kind="Program",
    description="Offshore drilling program with formation tops, casing, mud, "
                "BHA, full hydraulics recommendation (nozzles/TFA/HSI/ECD) "
                "and completion — modeled on Siri / Dorood drilling programs.",
    inputs=OFFSHORE_DRILLING_INPUTS,
    markdown=OFFSHORE_DRILLING_MD,
    meta={"category": "Programs", "new": True},
)

# ----------------------------------------------------------------------------
# ALL OFFSHORE TEMPLATES
# ----------------------------------------------------------------------------

OFFSHORE_TEMPLATES = [
    REENTRY_TEMPLATE,
    OFFSHORE_WORKOVER_TEMPLATE,
    OFFSHORE_DRILLING_TEMPLATE,
]
