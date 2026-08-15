# ============================================================================
# PROGRAM TEMPLATE LIBRARY
# ============================================================================
# Base program templates built from worldwide drilling/workover practice
# (API RP 5C3/10B/13B/53/59, ISO 10400/10426, NORSOK D-010, IADC, Shell DEP,
# Saudi Aramco SAES, BP GP). Placeholders use {{key}} syntax.
# ============================================================================

from typing import List
from wizard_engine import TemplateDef, InputSpec

# ----------------------------------------------------------------------------
# 1. DRILLING PROGRAM (NEW WELL)
# ----------------------------------------------------------------------------

DRILLING_PROGRAM_MD = r"""
# DRILLING PROGRAM — {{well_name}}

**Field:** {{field_name}} | **Operator:** {{operator}} | **Contractor:** {{contractor}}
**Rig:** {{rig_name}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## DOCUMENT CONTROL

| Item | Detail |
|---|---|
| Well | {{well_name}} |
| Field | {{field_name}} |
| Operator | {{operator}} |
| Contractor | {{contractor}} |
| Rig | {{rig_name}} |
| Well Type | {{well_type}} |
| Well Profile | {{well_profile}} |
| Total Depth (MD) | {{td_md}} |
| Total Depth (TVD) | {{td_tvd}} |
| Target Formation | {{target_formation}} |
| Prepared By | {{prepared_by}} |
| Reviewed By | {{reviewed_by}} |
| Approved By | {{approved_by}} |
| Revision | {{revision}} |
| Date | {{doc_date}} |

## 1. SCOPE AND OBJECTIVE

### 1.1 Scope

This program covers the complete drilling and completion of well **{{well_name}}** in the **{{field_name}}** field, including:

1. Rig move, rig-up and pre-spud checks.
2. Drilling all hole sections and running/cementing all casing strings.
3. Directional control and surveys as required.
4. Formation evaluation (logging, coring, DST as applicable).
5. Running the completion and well testing.
6. Securing the well and releasing the rig.

### 1.2 Objective

- Drill the well to the planned target depth safely and efficiently.
- Zero HSE incidents; no uncontrolled release of formation fluids.
- Meet the geological and reservoir objectives ({{target_formation}}).
- Complete the well ready for production/injection per design.
- Minimize NPT through thorough pre-job planning and offset-well learning.

### 1.3 Reference Documents

- Client technical specifications and applicable local regulations
- Offset well DDR / EOWR and lessons learned
- API RP 5C3, API RP 10B, API RP 13B, API RP 53, API RP 59
- IADC drilling guidelines; company HSE management system
- Vendor operating manuals (bits, BHA, mud, cement, wellhead, logging)

## 2. WELL DATA SUMMARY

| Parameter | Value |
|---|---|
| Field | {{field_name}} |
| Well | {{well_name}} |
| Well Type | {{well_type}} |
| Well Profile | {{well_profile}} |
| Ground Elevation | {{ground_elevation}} |
| Rotary/KB Elevation | {{kb_elevation}} |
| Total Depth MD | {{td_md}} |
| Total Depth TVD | {{td_tvd}} |
| Target Formation | {{target_formation}} |
| Reservoir Pressure | {{reservoir_pressure}} |
| Reservoir Temperature | {{reservoir_temperature}} |
| H2S Expected | {{h2s}} |
| CO2 Expected | {{co2}} |
| Mud Type (reservoir) | {{mud_type}} |

## 3. FORMATION TOPS & HAZARDS (PROGNOSIS)

{{formations_table}}

### Anticipated Hazards

{{hazards_table}}

## 4. CASING & HOLE PROGRAM

{{casing_table}}

### Casing Design Basis

- Design method: deterministic per API RP 5C3 / ISO 10400.
- Minimum design factors: burst 1.10, collapse 1.10, tension 1.60 (per local standard).
- Burst scenario: gas kick / full evacuation at shoe.
- Collapse scenario: full evacuation / lost returns.
- Connections selected for sealability and galling resistance (NACE MR-0175 if sour).

## 5. DRILLING FLUID PROGRAM

| Section | Type | MW In (ppg) | MW Out (ppg) | Remarks |
|---|---|---|---|---|
{{mud_table}}

- Maintain solids control equipment running at all times.
- Record mud properties every 30 minutes while circulating and per tour.
- LCM material and hi-vis pills to be available at all times.

## 6. BHA & DRILLING PARAMETERS

{{bha_table}}

| Section | WOB (klbs) | RPM | Flow (GPM) | Max SPP (psi) | Remarks |
|---|---|---|---|---|---|
{{drilling_params_table}}

- Stick to the recommended parameters; any change requires approval.
- Monitor torque, drag, ROP and ECD continuously.
- Break circulation before connections; ream down/up as required.

## 7. CEMENTING PROGRAM

{{cement_table}}

- Cement to surface where specified; verify full returns.
- WOC per slurry design; then pressure test shoe per test matrix.
- CBL/VDL where required before drilling out.

## 8. DIRECTIONAL PLAN

- Survey tool: {{survey_tool}}
- KOP: {{kop}} — Build rate: {{build_rate}} — Hold: {{hold_inclination}}° / {{hold_azimuth}}°
- Max DLS: {{max_dls}} °/100ft
- Anti-collision check against offset wells before spud and per section.

## 9. BOP & WELL CONTROL

- BOP stack: {{bop_stack}} rated {{bop_rating}} psi.
- Test BOP per API RP 53: low 250 psi, high 70% of rated WP ({{bop_test_pressure}} psi), hold 10-15 min.
- Slow pump rates recorded per section.
- Well control drills: weekly; H2S drill: {{h2s_drills}}.
- Kick tolerance / MAASP: {{maasp}} psi at shoe.

## 10. TIME ESTIMATE

| Phase | Duration (days) | Cumulative (days) |
|---|---|---|
{{time_table}}

**Total estimated:** {{total_days}} days (excl. NPT contingency {{npt_contingency}}%).

## 11. HSE REQUIREMENTS

- Pre-spud safety meeting and rig HSE audit before operations.
- PPE mandatory; task-specific risk assessments (TRA) for all non-routine jobs.
- Emergency response plan, muster points and drills.
- H2S monitoring and BA/SCBA readiness {{h2s}}.
- Waste management per local regulation; zero-discharge where applicable.

## 12. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Pre-spud | BOP and wellhead tested; rig audit passed |
| HP-02 | Per section | LOT/FIT accepted; casing and cement program confirmed |
| HP-03 | Before drilling out | Shoe test accepted |
| HP-04 | TD | TD confirmed; logging program accepted |
| HP-05 | Completion | Completion design confirmed; wellhead tested |

## 13. CONTINGENCIES

- **Lost circulation:** LCM pills, cement plugs; if severe — set casing early.
- **Kick:** shut in, strip, circulate per Driller's/Wait & Weight method.
- **Stuck pipe:** work pipe within limits, jarring, spotting; fishing as last resort.
- **H2S:** activate emergency plan, evacuate upwind, monitor continuously.

## 14. CHECKLISTS

### Pre-Spud Checklist

- [ ] Rig inspected and level
- [ ] BOP tested and certified
- [ ] Wellhead installed and tested
- [ ] Mud system and chemicals on location
- [ ] Casing, bits and tools on location and inspected
- [ ] Surveys/anti-collision approved
- [ ] H2S equipment and BA sets ready
- [ ] Emergency drills completed
- [ ] Safety meeting held with all crews

### Per-Section Checklist

- [ ] Casing tally and running equipment ready
- [ ] Cement program and lab results approved
- [ ] Shoe track and float equipment tested
- [ ] Torque gauge calibrated
- [ ] Drilling parameters reviewed with crew

## 15. APPENDICES

- Appendix A: Well schematic
- Appendix B: Casing tally & cement volumes
- Appendix C: BOP stack diagram
- Appendix D: Torque tables
- Appendix E: Kill sheet
- Appendix F: Daily report template
- Appendix G: Bit record / BHA records

## DOCUMENT APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Reviewed By (Engineering) | {{reviewed_by}} | | |
| Approved By (Management) | {{approved_by}} | | |
"""

DRILLING_PROGRAM = TemplateDef(
    key="drilling_program",
    name="Drilling Program (New Well)",
    icon="🛢️",
    kind="Program",
    description=(
        "Complete drilling program for a new well: scope, well data, "
        "formations, casing, mud, BHA, cement, directional, BOP, time "
        "estimate, HSE, hold points, contingencies and checklists."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  placeholder="e.g. WELL-101", group="Well & Company"),
        InputSpec("field_name", "Field Name", "text", group="Well & Company"),
        InputSpec("operator", "Operator", "text", group="Well & Company"),
        InputSpec("contractor", "Contractor", "text", group="Well & Company"),
        InputSpec("rig_name", "Rig Name / Type", "text",
                  placeholder="e.g. Rig 45 (1000 HP)", group="Well & Company"),
        InputSpec("well_type", "Well Type", "combo",
                  options=["Development", "Exploration", "Appraisal",
                           "Injection", "Observation", "Sidetrack"],
                  group="Well & Company"),
        InputSpec("well_profile", "Well Profile", "combo",
                  options=["Vertical", "Directional J-Type",
                           "Directional S-Type", "Horizontal", "ERD"],
                  group="Well & Company"),
        InputSpec("td_md", "Total Depth MD", "number", unit="m",
                  required=True, group="Well & Company"),
        InputSpec("td_tvd", "Total Depth TVD", "number", unit="m",
                  group="Well & Company"),
        InputSpec("ground_elevation", "Ground Elevation", "number", unit="m",
                  group="Well & Company"),
        InputSpec("kb_elevation", "KB / RT Elevation", "number", unit="m",
                  group="Well & Company"),
        InputSpec("target_formation", "Target Formation", "text",
                  group="Reservoir"),
        InputSpec("reservoir_pressure", "Reservoir Pressure", "number",
                  unit="psi", group="Reservoir"),
        InputSpec("reservoir_temperature", "Reservoir Temperature", "number",
                  unit="°F", group="Reservoir"),
        InputSpec("h2s", "H2S Expected", "combo", options=["NO", "YES",
                  "YES - up to 5%", "YES - >5%"], group="Reservoir"),
        InputSpec("co2", "CO2 Expected", "text", placeholder="%",
                  group="Reservoir"),
        InputSpec("mud_type", "Reservoir Mud Type", "combo",
                  options=["WBM - KCl Polymer", "OBM - Diesel Based",
                           "OBM - Mineral Oil", "SBM", "Brine"],
                  group="Reservoir"),
        InputSpec("formations_table", "Formation Tops (Name / MD / TVD / PP / FG)",
                  "table", columns=["Formation", "MD Top (m)", "MD Bottom (m)",
                                    "PP (ppg)", "FG (ppg)", "Remarks"],
                  group="Geology"),
        InputSpec("hazards_table", "Anticipated Hazards",
                  "table", columns=["Hazard", "Interval (m)", "Severity",
                                    "Mitigation"],
                  group="Geology"),
        InputSpec("casing_table", "Casing Program",
                  "table", columns=["Hole (in)", "Casing (in)", "Grade",
                                    "Wt (ppf)", "Conn", "Set Depth (m)",
                                    "TOC (m)"],
                  required=True, group="Casing & Mud"),
        InputSpec("mud_table", "Mud Program per Section",
                  "table", columns=["Section", "Type", "MW in (ppg)",
                                    "MW out (ppg)", "Remarks"],
                  group="Casing & Mud"),
        InputSpec("cement_table", "Cement Program",
                  "table", columns=["Section", "Lead (ppg/bbl)", "Tail (ppg/bbl)",
                                    "TOC (m)", "Excess %", "WOC (hr)"],
                  group="Casing & Mud"),
        InputSpec("bha_table", "BHA Plan",
                  "table", columns=["Section", "Bit Type", "Bit Size (in)",
                                    "BHA Type", "MWD/LWD"],
                  group="Drilling"),
        InputSpec("drilling_params_table", "Drilling Parameters",
                  "table", columns=["Section", "WOB (klbs)", "RPM",
                                    "Flow (GPM)", "Max SPP (psi)"],
                  group="Drilling"),
        InputSpec("survey_tool", "Survey Tool", "combo",
                  options=["MWD", "Gyro MWD", "Gyro While Drilling",
                           "Single Shot", "Multi-Shot"], group="Drilling"),
        InputSpec("kop", "KOP (MD)", "text", placeholder="m",
                  group="Drilling"),
        InputSpec("build_rate", "Build Rate", "number", unit="°/100ft",
                  group="Drilling"),
        InputSpec("hold_inclination", "Hold Inclination", "number", unit="°",
                  group="Drilling"),
        InputSpec("hold_azimuth", "Hold Azimuth", "number", unit="°",
                  group="Drilling"),
        InputSpec("max_dls", "Max DLS", "number", unit="°/100ft",
                  group="Drilling"),
        InputSpec("bop_stack", "BOP Stack", "combo",
                  options=["Annular + Double Ram + Single Ram",
                           "Annular + Triple Ram", "Quad Ram",
                           "Subsea Stack"], group="Well Control"),
        InputSpec("bop_rating", "BOP Rating", "combo", options=["5000",
                  "10000", "15000", "20000"], unit="psi", group="Well Control"),
        InputSpec("bop_test_pressure", "BOP Test Pressure", "number",
                  unit="psi", group="Well Control"),
        InputSpec("maasp", "MAASP at Shoe", "number", unit="psi",
                  group="Well Control"),
        InputSpec("h2s_drills", "H2S Drills Frequency", "combo",
                  options=["Weekly", "Monthly", "Per Tour"], group="HSE"),
        InputSpec("time_table", "Time Estimate per Phase",
                  "table", columns=["Phase", "Duration (days)", "Remarks"],
                  group="Time"),
        InputSpec("total_days", "Total Estimated Days", "number", unit="days",
                  group="Time"),
        InputSpec("npt_contingency", "NPT Contingency", "number", unit="%",
                  default="10", group="Time"),
    ],
    markdown=DRILLING_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 2. WORKOVER PROGRAM (GENERAL)
# ----------------------------------------------------------------------------

WORKOVER_PROGRAM_MD = r"""
# WORKOVER PROGRAM — {{well_name}}

**Field:** {{field_name}} | **Contractor:** {{contractor}} | **Rig:** {{rig_name}}
**Revision:** {{revision}} | **Date:** {{doc_date}}

## DOCUMENT CONTROL

| Item | Detail |
|---|---|
| Well | {{well_name}} |
| Field | {{field_name}} |
| Rig | {{rig_name}} |
| Client | {{operator}} |
| Contractor | {{contractor}} |
| Workover Type | {{workover_type}} |
| Prepared By | {{prepared_by}} |
| Reviewed By | {{reviewed_by}} |
| Approved By | {{approved_by}} |
| Revision | {{revision}} |
| Date | {{doc_date}} |

## 1. SCOPE AND OBJECTIVE

### 1.1 Scope

This program covers the complete workover of well **{{well_name}}** to:

1. Kill the well safely ({{kill_method}}).
2. Retrieve the existing completion / equipment.
3. Perform required remedial work: {{remedial_scope}}.
4. Run the new completion ({{completion_description}}).
5. Test, hand over the well and release the rig.

### 1.2 Objective

- Restore / improve well integrity and productivity.
- Zero HSE incidents.
- Minimum NPT through pre-job planning and readiness.
- Full documentation of tests, hold points and handover data.

### 1.3 Reference Documents

- Original drilling/completion program and DDR
- Well file / wellhead records and schematics
- Vendor procedures (packer, TRSV/SSD, ESP, wellhead)
- Company HSE management system; local regulations

## 2. WELL DATA SUMMARY

| Parameter | Value |
|---|---|
| Well | {{well_name}} |
| Field | {{field_name}} |
| Completion Type | {{completion_description}} |
| Producing Interval | {{producing_interval}} |
| Reservoir Pressure | {{reservoir_pressure}} |
| H2S | {{h2s}} |
| Wellhead Pressures (Tbg/Ann) | {{wellhead_pressures}} |
| Critical Depths (packer/SSD/TRSV) | {{critical_depths}} |

## 3. ORGANIZATION & RESPONSIBILITIES

| Role | Responsibilities |
|---|---|
| Company WO Supervisor | Overall control, safety, approvals |
| Rig Supervisor | Rig operations and crew |
| Completion Engineer | Design verification, hold points |
| Service Supervisors | Vendor operations per procedure |
| HSE Officer | Permits, drills, compliance |

## 4. SERVICES REQUIRED

{{services_table}}

## 5. EQUIPMENT & MATERIALS

{{equipment_table}}

## 6. EXECUTION PROCEDURE

### Phase 1 — Preparation & Rig-Up ({{phase1_time}})

1. Rig move and rig-up; level and secure rig.
2. Record wellhead pressures (tubing + all annuli); verify well status.
3. Rig up and pressure test surface lines ({{surface_test_pressure}} psi).
4. Stand back required tubulars; wash, drift and measure.
5. Pre-job safety meeting with all crews.

### Phase 2 — Kill the Well ({{phase2_time}})

1. Rig up slickline; pressure test SL BOP {{sl_bop_test}} psi.
2. Run plugs/barriers as per kill plan: {{kill_barriers}}.
3. Kill the well by: {{kill_method}} using {{kill_fluid}}.
4. Monitor pressures; confirm well dead (shut-in {{kill_confirm_minutes}} minutes).
5. Install secondary barrier ({{secondary_barrier}}) before pulling.

### Phase 3 — Pull Existing Completion ({{phase3_time}})

1. N/D XMT; install TWCV; test {{twcv_test}} psi.
2. N/U BOP stack; pressure test per matrix.
3. Connect landing joint; verify well static.
4. Unset packer per OEM procedure; POOH completion.
5. Lay down and inspect all components; protect threads.
6. **All retrieved tools to inspection workshop immediately.**

### Phase 4 — Remedial / Preparatory Work ({{phase4_time}})

{{remedial_scope}}

1. Run scraper/drift per requirements: {{scraper_sizes}}.
2. Perform remedial operations (cement, RTTS, fishing, logging, milling)
   as listed in Section 6.5.

### Phase 5 — Run New Completion ({{phase5_time}})

1. Pre-run verification gate: all tools, XOs, tubing tallied and tested.
2. Run completion per design: {{completion_description}}.
3. Test at intermediate depths per test matrix ({{string_test_pressure}} psi).
4. Set packer ({{packer_setting_pressure}} psi); test annulus
   {{annulus_test_pressure}} psi.
5. Land hanger; install wellhead; test {{wellhead_test_pressure}} psi.

### Phase 6 — Completion / Well Test ({{phase6_time}})

1. Retrieve plugs; function test TRSV/SSD.
2. Flow well / test per program.
3. Secure well; hand over.

## 7. HOLD POINTS

| HP | Phase | Hold Point |
|---|---|---|
| HP-01 | 2 | Before opening well (kill plan approved) |
| HP-02 | 3 | BOP tested and accepted |
| HP-03 | 3 | Before pulling — well confirmed dead |
| HP-04 | 4 | Remedial work results reviewed |
| HP-05 | 5 | Completion tools verified / packer set & tested |
| HP-06 | 6 | Wellhead tested / well handed over |

## 8. TEST MATRIX

| Item | Test Pressure (psi) | Hold (min) | Witness |
|---|---|---|---|
| Surface lines | {{surface_test_pressure}} | 15 | Co. WO |
| SL BOP | {{sl_bop_test}} | 10 | Co. WO |
| BOP stack | {{bop_test_pressure}} | 15 | Co. WO + Client |
| TWCV | {{twcv_test}} | 15 | Co. WO |
| String (intermediate) | {{string_test_pressure}} | 15 | Co. WO |
| Packer / annulus | {{annulus_test_pressure}} | 15 | Co. WO + Client |
| Wellhead / XMT | {{wellhead_test_pressure}} | 15 | Co. WO + Client |

## 9. CONTINGENCY PLANS

- **Cannot kill well:** bullhead, CT, or dynamic kill per plan; escalate to
  Client.
- **Packer stuck:** jarring/overpull within limits, E-backoff, mill out.
- **Stuck tubing:** work pipe, back-off, fishing; cement plug below before
  milling if permanent packer.
- **Leaking test:** re-torque, re-test, replace with backup.
- **H2S / weather delays:** follow HSE plan; winterize if required.

## 10. HSE REQUIREMENTS

- Pre-job HSE audit and safety meeting.
- Permit to work system for all non-routine jobs.
- H2S monitoring with BA/SCBA {{h2s}}.
- Emergency drills and muster before operations.
- PPE and lifting certificates valid.

## 11. CHECKLISTS

### Pre-Mobilization

- [ ] Well file and last EOWR reviewed
- [ ] Wellhead and completion drawings confirmed
- [ ] All services contracted
- [ ] Tubulars and tools inspected
- [ ] Kill fluid and additives on location
- [ ] Contingency plans documented

### Pre-Workover

- [ ] Wellhead pressures recorded
- [ ] Lines pressure tested
- [ ] BOP tested
- [ ] H2S equipment ready
- [ ] Safety meeting held

## 12. APPENDICES

- Appendix A: Completion diagram (new & existing)
- Appendix B: Tubing tally
- Appendix C: Wellhead drawing
- Appendix D: Kill sheet
- Appendix E: Test forms
- Appendix F: Daily report template

## DOCUMENT APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Reviewed By (Engineering) | {{reviewed_by}} | | |
| Approved By (Management) | {{approved_by}} | | |
| Approved By (Client) | | | |
"""

WORKOVER_PROGRAM = TemplateDef(
    key="workover_program",
    name="Workover Program (General)",
    icon="🔧",
    kind="Program",
    description=(
        "Complete workover program: kill, pull existing completion, "
        "remedial work, run new completion, test and hand over."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  placeholder="e.g. WELL-205", group="Well & Company"),
        InputSpec("field_name", "Field Name", "text", group="Well & Company"),
        InputSpec("operator", "Client", "text", group="Well & Company"),
        InputSpec("contractor", "Contractor", "text", group="Well & Company"),
        InputSpec("rig_name", "Rig Name / Type", "text",
                  placeholder="e.g. Rig 12 (Truck Mounted 1000HP)",
                  group="Well & Company"),
        InputSpec("workover_type", "Workover Type", "combo",
                  options=["ESP Replacement", "Completion Repair",
                           "Well Integrity / Casing Repair", "Re-perforation",
                           "Stimulation", "Convert to Injection",
                           "Retrieve stuck fish", "Other"],
                  required=True, group="Scope"),
        InputSpec("completion_description", "New Completion Description",
                  "textarea", placeholder="e.g. ESP completion with 4-1/2\" "
                  "tubing, TRSV, SSD, packer",
                  group="Scope"),
        InputSpec("producing_interval", "Producing Interval", "text",
                  placeholder="e.g. 2450-2500 m MD",
                  group="Well Data"),
        InputSpec("reservoir_pressure", "Reservoir Pressure", "number",
                  unit="psi", group="Well Data"),
        InputSpec("h2s", "H2S", "combo", options=["NO", "YES", "YES - up to 5%",
                  "YES - >5%"], group="Well Data"),
        InputSpec("wellhead_pressures", "Wellhead Pressures (Tbg / Ann)",
                  "text", placeholder="e.g. 0 / 450 psi",
                  group="Well Data"),
        InputSpec("critical_depths", "Critical Depths", "text",
                  placeholder="e.g. packer 2350m, SSD 2300m, TRSV 100m",
                  group="Well Data"),
        InputSpec("kill_method", "Kill Method", "combo",
                  options=["Reverse circulation via SSD", "Bullhead",
                           "Coil Tubing", "Circulation (forward)"],
                  group="Kill"),
        InputSpec("kill_fluid", "Kill Fluid", "text",
                  placeholder="e.g. DME emulsion 8.6 ppg / brine 9.2 ppg",
                  group="Kill"),
        InputSpec("kill_barriers", "Barriers Before Pulling", "textarea",
                  placeholder="e.g. plug in SSD + TRSV closed + TWCV",
                  group="Kill"),
        InputSpec("secondary_barrier", "Secondary Barrier", "text",
                  placeholder="e.g. TWCV / BOP",
                  group="Kill"),
        InputSpec("kill_confirm_minutes", "Kill Confirmation Shut-in", "number",
                  unit="min", default="30", group="Kill"),
        InputSpec("remedial_scope", "Remedial Scope", "textarea",
                  placeholder="e.g. corrosion log, THS change, squeeze, "
                  "scrape and drift", group="Remedial"),
        InputSpec("scraper_sizes", "Scraper / Mill Sizes", "text",
                  placeholder="e.g. 9-5/8\" + 7\" tandem scraper",
                  group="Remedial"),
        InputSpec("sl_bop_test", "SL BOP Test", "number", unit="psi",
                  default="2500", group="Tests"),
        InputSpec("surface_test_pressure", "Surface Lines Test", "number",
                  unit="psi", default="5000", group="Tests"),
        InputSpec("bop_test_pressure", "BOP Test Pressure", "number",
                  unit="psi", default="5000", group="Tests"),
        InputSpec("twcv_test", "TWCV Test", "number", unit="psi",
                  default="4500", group="Tests"),
        InputSpec("string_test_pressure", "String Test Pressure", "number",
                  unit="psi", default="3500", group="Tests"),
        InputSpec("annulus_test_pressure", "Packer/Annulus Test", "number",
                  unit="psi", default="1000", group="Tests"),
        InputSpec("packer_setting_pressure", "Packer Setting Pressure",
                  "number", unit="psi", default="3500", group="Tests"),
        InputSpec("wellhead_test_pressure", "Wellhead/XMT Test", "number",
                  unit="psi", default="4500", group="Tests"),
        InputSpec("phase1_time", "Phase 1 Duration", "text", default="48 hrs",
                  group="Time"),
        InputSpec("phase2_time", "Phase 2 Duration", "text", default="24 hrs",
                  group="Time"),
        InputSpec("phase3_time", "Phase 3 Duration", "text", default="60 hrs",
                  group="Time"),
        InputSpec("phase4_time", "Phase 4 Duration", "text", default="72 hrs",
                  group="Time"),
        InputSpec("phase5_time", "Phase 5 Duration", "text", default="80 hrs",
                  group="Time"),
        InputSpec("phase6_time", "Phase 6 Duration", "text", default="48 hrs",
                  group="Time"),
        InputSpec("services_table", "Services Required",
                  "table", columns=["Service", "Scope", "Mob Timing",
                                    "Company"],
                  group="Services & Equipment"),
        InputSpec("equipment_table", "Key Equipment & Materials",
                  "table", columns=["Item", "Specification", "Qty", "Remarks"],
                  group="Services & Equipment"),
    ],
    markdown=WORKOVER_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 3. ESP WORKOVER PROGRAM (from the master execution document)
# ----------------------------------------------------------------------------

ESP_WORKOVER = TemplateDef(
    key="esp_workover",
    name="ESP Workover Program",
    icon="⚡",
    kind="Program",
    description=(
        "Master Execution Document for running an ESP completion — kill, "
        "decompletion, corrosion logging, THS change, cleanout, ESP run, "
        "splice, wellhead, test and release. Based on the South Azadegan "
        "ESP workover master document."),
    source_file="ESP_Completion_Workover_Master_Execution.md",
    tokens={
        "WELL-XXX": "well_name",
        "South Azadegan": "field_name",
        "[To Be Confirmed]": "tbc",
        "[Name / Title]": "prepared_by",
        "[m]": "depth_m",
        "[psi]": "pressure_psi",
        "[bbl]": "volume_bbl",
        "[%]": "percent",
        "[model]": "model",
        "[qty]": "qty",
        "[volume]": "volume",
        "[tons]": "tons",
    },
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  default="WELL-XXX", group="Well"),
        InputSpec("field_name", "Field", "text", default="South Azadegan",
                  group="Well"),
        InputSpec("tbc", "To Be Confirmed items (rig, client, pads, dates...)",
                  "text", placeholder="Fill once — replaces all "
                  "'[To Be Confirmed]' entries", group="Well"),
        InputSpec("prepared_by", "Prepared By (Name / Title)", "text",
                  group="Well"),
        InputSpec("depth_m", "Depths (m) — fill once for all '[m]' entries",
                  "text", placeholder="e.g. 2450", group="Numbers"),
        InputSpec("pressure_psi", "Pressures (psi) — fill once for '[psi]'",
                  "text", placeholder="e.g. 3500", group="Numbers"),
        InputSpec("volume_bbl", "Volumes (bbl) — fill once for '[bbl]'",
                  "text", placeholder="e.g. 125", group="Numbers"),
        InputSpec("percent", "Percent (%) — fill once for '[%]'",
                  "text", placeholder="e.g. 4.2", group="Numbers"),
        InputSpec("model", "Equipment Models — fill once for '[model]'",
                  "text", group="Numbers"),
        InputSpec("qty", "Quantities — fill once for '[qty]'",
                  "text", group="Numbers"),
    ],
)

# ----------------------------------------------------------------------------
# 4. WELL ABANDONMENT (P&A) PROGRAM
# ----------------------------------------------------------------------------

ABANDONMENT_PROGRAM_MD = r"""
# WELL ABANDONMENT PROGRAM (P&A) — {{well_name}}

**Field:** {{field_name}} | **Contractor:** {{contractor}} | **Rig:** {{rig_name}}
**Revision:** {{revision}} | **Date:** {{doc_date}}

## DOCUMENT CONTROL

| Item | Detail |
|---|---|
| Well | {{well_name}} |
| Field | {{field_name}} |
| Rig | {{rig_name}} |
| Operator | {{operator}} |
| Abandonment Type | {{abandonment_type}} |
| Prepared By | {{prepared_by}} |
| Reviewed By | {{reviewed_by}} |
| Approved By | {{approved_by}} |
| Revision | {{revision}} |
| Date | {{doc_date}} |

## 1. SCOPE AND OBJECTIVE

### 1.1 Scope

Permanent abandonment (P&A) of well **{{well_name}}** in accordance with
local regulations and international standards (NORSOK D-010 / local
regulatory requirements), including:

1. Kill the well and establish well control barriers.
2. Pull tubulars and completion equipment.
3. Set permanent cement plugs at specified depths.
4. Cut and retrieve casing where required; install surface plugs.
5. Cut off casing below ground / seabed and install cap.
6. Verify barriers and document for handover.

### 1.2 Objective

- Establish and verify **two independent well barriers** for all time.
- Protect fresh-water aquifers; isolate all hydrocarbon-bearing zones.
- Leave the location clean and the well in a permanently safe condition.
- Full documentation (as-built) for regulatory close-out.

### 1.3 Barrier Philosophy

- Barrier element: cement plug with verified length/placement, or verified
  mechanical barrier + cement.
- Each barrier tested (pressure test or inflow test) and documented.
- Barrier depths selected against formation/lithology and pore pressure.

## 2. WELL DATA & ABANDONMENT PLAN

| Parameter | Value |
|---|---|
| Well | {{well_name}} |
| Field | {{field_name}} |
| TD | {{td_md}} |
| Production Interval | {{producing_interval}} |
| Reservoir Pressure | {{reservoir_pressure}} |
| H2S | {{h2s}} |
| Current Completion | {{completion_summary}} |

### Planned Cement Plugs

{{plugs_table}}

## 3. EXECUTION PROCEDURE

### Phase 1 — Rig-Up & Well Preparation

1. Rig up; record wellhead pressures; verify well status.
2. Kill well with {{kill_fluid}}; confirm dead.
3. N/D XMT; install BOP; pressure test {{bop_test_pressure}} psi.

### Phase 2 — Pull Completion

1. Set plugs / barriers as required ({{barriers}}).
2. POOH completion; lay down; inspect.
3. Run drift/gauge to confirm access.

### Phase 3 — Cement Plugs

1. RIH cementing string on {{cementing_string}}.
2. Set plug #1 at {{plug1_depth}} (below production interval) with
   {{cement_slurry}} slurry; volume {{plug1_volume}}.
3. POOH above plug; WOC {{woc_time}} hrs.
4. Tag and pressure test plug #1: {{plug1_test}} psi.
5. Repeat for subsequent plugs per {{plugs_table}}.
6. Set environmental/ surface plug at {{surface_plug_depth}}.

### Phase 4 — Casing Cut & Retrieval

1. Cut casing at {{cut_depth}} per approved procedure (permit required).
2. Retrieve casing above cut; inspect.
3. Set surface cap / plate and weld as per drawing.

### Phase 5 — Location Restoration

1. Remove all equipment; clean location.
2. Restore surface per regulation.
3. Submit as-built abandonment report.

## 4. BARRIER VERIFICATION

| Barrier | Depth | Type | Verification |
|---|---|---|---|
| B1 (primary) | {{plug1_depth}} | Cement plug | Pressure test {{plug1_test}} psi |
| B2 (secondary) | {{plug2_depth}} | Cement plug / mechanical | Test / tagged |

- Inflow test where applicable ({{inflow_test}}).
- All results recorded on the barrier verification form.

## 5. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Kill | Well confirmed dead |
| HP-02 | Plugs | Plug #1 tagged and tested |
| HP-03 | Plugs | All plugs tested and accepted |
| HP-04 | Casing | Casing cut approved and completed |
| HP-05 | Close-out | As-built documentation approved |

## 6. HSE REQUIREMENTS

- Permit to work for cutting, welding and lifting.
- H2S monitoring {{h2s}}; gas testing during all operations.
- Dropped-object prevention during casing cutting.
- Environmental compliance for fluids and cuttings.

## 7. CHECKLISTS

- [ ] Kill fluid available and tested
- [ ] Cement lab test approved (slurry {{cement_slurry}})
- [ ] Casing cut permit obtained
- [ ] Barrier verification forms ready
- [ ] Regulator notified per requirement

## DOCUMENT APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Reviewed By | {{reviewed_by}} | | |
| Approved By (Management) | {{approved_by}} | | |
| Approved By (Regulator) | | | |
"""

ABANDONMENT_PROGRAM = TemplateDef(
    key="abandonment_program",
    name="Well Abandonment Program (P&A)",
    icon="🚫",
    kind="Program",
    description=(
        "Permanent plug & abandonment program: kill, pull completion, "
        "cement plugs, casing cut, surface restoration and barrier "
        "verification (NORSOK D-010 based)."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  group="Well"),
        InputSpec("field_name", "Field", "text", group="Well"),
        InputSpec("operator", "Operator", "text", group="Well"),
        InputSpec("contractor", "Contractor", "text", group="Well"),
        InputSpec("rig_name", "Rig / Unit", "text", group="Well"),
        InputSpec("abandonment_type", "Abandonment Type", "combo",
                  options=["Permanent (P&A)", "Suspended (Temporary)",
                           "Sidetrack & Abandon"],
                  group="Well"),
        InputSpec("td_md", "TD (MD)", "number", unit="m", group="Well Data"),
        InputSpec("producing_interval", "Production Interval", "text",
                  group="Well Data"),
        InputSpec("reservoir_pressure", "Reservoir Pressure", "number",
                  unit="psi", group="Well Data"),
        InputSpec("h2s", "H2S", "combo", options=["NO", "YES"],
                  group="Well Data"),
        InputSpec("completion_summary", "Current Completion", "textarea",
                  group="Well Data"),
        InputSpec("kill_fluid", "Kill Fluid", "text", group="Kill"),
        InputSpec("barriers", "Barriers Before Pulling", "text",
                  group="Kill"),
        InputSpec("plugs_table", "Planned Cement Plugs",
                  "table", columns=["Plug #", "Depth (m)", "Interval (m)",
                                    "Slurry", "Volume (bbl)", "Test (psi)"],
                  required=True, group="Plugs"),
        InputSpec("plug1_depth", "Plug #1 Depth", "number", unit="m",
                  group="Plugs"),
        InputSpec("plug1_volume", "Plug #1 Volume", "number", unit="bbl",
                  group="Plugs"),
        InputSpec("plug1_test", "Plug #1 Test Pressure", "number", unit="psi",
                  default="1000", group="Plugs"),
        InputSpec("plug2_depth", "Plug #2 Depth", "number", unit="m",
                  group="Plugs"),
        InputSpec("cement_slurry", "Cement Slurry", "combo",
                  options=["Class G 15.8 ppg", "Class G + silica 16.4 ppg",
                           "Class H 16.0 ppg", "Micro-cement"],
                  group="Plugs"),
        InputSpec("woc_time", "WOC Time", "number", unit="hrs", default="12",
                  group="Plugs"),
        InputSpec("cementing_string", "Cementing String", "text",
                  default="3-1/2\" DP", group="Plugs"),
        InputSpec("surface_plug_depth", "Surface Plug Depth", "number",
                  unit="m", group="Plugs"),
        InputSpec("cut_depth", "Casing Cut Depth", "number", unit="m",
                  group="Casing"),
        InputSpec("inflow_test", "Inflow Test Required", "combo",
                  options=["YES", "NO"], group="Casing"),
        InputSpec("bop_test_pressure", "BOP Test Pressure", "number",
                  unit="psi", default="3000", group="Tests"),
    ],
    markdown=ABANDONMENT_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 5. WELL KILL PROGRAM
# ----------------------------------------------------------------------------

WELL_KILL_PROGRAM_MD = r"""
# WELL KILL OPERATION PROGRAM — {{well_name}}

**Field:** {{field_name}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Kill well **{{well_name}}** safely by {{kill_method}} using
**{{kill_fluid}}** (density {{kill_fluid_weight}}) with zero losses and zero
HSE incidents, to allow subsequent operations: {{next_operation}}.

## 2. PRE-KILL DATA

| Parameter | Value |
|---|---|
| Well | {{well_name}} |
| Current Tubing Pressure | {{tubing_pressure}} psi |
| Current Annulus Pressure | {{annulus_pressure}} psi |
| Reservoir Pressure (at datum {{datum_depth}} m) | {{reservoir_pressure}} psi |
| Current Fluid in Hole | {{well_fluid}} |
| Kill Fluid | {{kill_fluid}} |
| Kill Fluid Weight | {{kill_fluid_weight}} ppg |
| Estimated Kill Volume | {{kill_volume}} bbl |
| MAASP (at shoe) | {{maasp}} psi |
| Fracture Pressure at Shoe | {{frac_pressure}} psi |

## 3. KILL SHEET (HYDROSTATIC CHECK)

| Item | Value |
|---|---|
| Hydrostatic of kill fluid at datum | {{kill_hydrostatic}} psi |
| Required overbalance | {{overbalance}} psi |
| Planned surface pressure during kill | {{kill_surface_pressure}} psi |
| Pump rate | {{pump_rate}} bpm |
| Estimated time | {{kill_time}} hrs |

- Overbalance target: {{overbalance}} psi (minimum 200 psi, maximum below
  fracture pressure at the shoe).
- If losses occur: reduce rate, use LCM pills, keep annulus topped up.

## 4. KILL PROCEDURE

### Method: {{kill_method}}

1. Line up as per rig floor diagram; test lines to {{line_test}} psi.
2. Ensure all personnel aware; H2S watch on {{h2s}}.
3. Record baseline pressures; open choke line to separator/pit as planned.
4. Pump kill fluid at {{pump_rate}} bpm while monitoring:
   - pump pressure (target {{kill_surface_pressure}} psi),
   - returns rate and pit level,
   - annulus pressure.
5. When kill fluid reaches the perforations/SSD: stop, shut in and observe
   {{shut_in_time}} minutes.
6. Confirm well dead (no flow, pressure stable). Bleed check per procedure.
7. If pressure builds again — repeat circulation; if losses — apply LCM /
   balanced pill; escalate to Client if unstable.

## 5. CONTINGENCIES

- **Cannot circulate (blocked path):** bullhead with Client approval.
- **Losses during kill:** reduce density (emulsion / nitrified fluid if
  allowed), LCM, hi-vis pills; monitor level.
- **Gas at surface:** divert via choke manifold; H2S plan activated.
- **Well flowing after kill:** maintain barriers, repeat kill with
  higher-weight fluid.

## 6. HSE & WELL CONTROL

- All well control equipment tested and certified.
- H2S monitoring and BA/SCBA ready {{h2s}}.
- No hot work during kill unless permitted.
- Continuous communication rig floor – choke manifold – office.

## 7. HOLD POINT

> **HP-01:** Well confirmed dead (shut-in {{shut_in_time}} min, no pressure
> build-up) — witnessed by Company Supervisor + Client before rigging down.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By (Operations) | {{approved_by}} | | |
"""

WELL_KILL_PROGRAM = TemplateDef(
    key="well_kill_program",
    name="Well Kill Operation Program",
    icon="🔴",
    kind="Program",
    description=(
        "Kill operation program with kill sheet: pre-kill data, hydrostatic "
        "check, step-by-step circulation/bullhead, contingencies and hold "
        "point."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  group="Well"),
        InputSpec("field_name", "Field", "text", group="Well"),
        InputSpec("next_operation", "Next Operation After Kill", "text",
                  placeholder="e.g. pull completion", group="Well"),
        InputSpec("tubing_pressure", "Tubing Pressure", "number", unit="psi",
                  group="Pre-Kill Data"),
        InputSpec("annulus_pressure", "Annulus Pressure", "number", unit="psi",
                  group="Pre-Kill Data"),
        InputSpec("reservoir_pressure", "Reservoir Pressure", "number",
                  unit="psi", group="Pre-Kill Data"),
        InputSpec("datum_depth", "Datum Depth", "number", unit="m",
                  group="Pre-Kill Data"),
        InputSpec("well_fluid", "Current Well Fluid", "text",
                  placeholder="e.g. crude + gas", group="Pre-Kill Data"),
        InputSpec("kill_method", "Kill Method", "combo",
                  options=["Reverse circulation via SSD", "Bullhead",
                           "Forward circulation", "Coil Tubing"],
                  group="Kill Design"),
        InputSpec("kill_fluid", "Kill Fluid", "text",
                  placeholder="e.g. DME emulsion / NaCl brine",
                  group="Kill Design"),
        InputSpec("kill_fluid_weight", "Kill Fluid Weight", "number",
                  unit="ppg", group="Kill Design"),
        InputSpec("kill_volume", "Estimated Kill Volume", "number", unit="bbl",
                  group="Kill Design"),
        InputSpec("kill_hydrostatic", "Kill Fluid Hydrostatic at Datum",
                  "number", unit="psi", group="Kill Design"),
        InputSpec("overbalance", "Required Overbalance", "number", unit="psi",
                  default="300", group="Kill Design"),
        InputSpec("kill_surface_pressure", "Planned Surface Pressure",
                  "number", unit="psi", group="Kill Design"),
        InputSpec("pump_rate", "Pump Rate", "number", unit="bpm",
                  default="2", group="Kill Design"),
        InputSpec("kill_time", "Estimated Kill Time", "number", unit="hrs",
                  group="Kill Design"),
        InputSpec("maasp", "MAASP at Shoe", "number", unit="psi",
                  group="Kill Design"),
        InputSpec("frac_pressure", "Fracture Pressure at Shoe", "number",
                  unit="psi", group="Kill Design"),
        InputSpec("line_test", "Line Test Pressure", "number", unit="psi",
                  default="3000", group="Execution"),
        InputSpec("shut_in_time", "Shut-in Confirmation Time", "number",
                  unit="min", default="30", group="Execution"),
        InputSpec("h2s", "H2S Present", "combo", options=["NO", "YES"],
                  group="HSE"),
    ],
    markdown=WELL_KILL_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 6. CEMENTING JOB PROGRAM
# ----------------------------------------------------------------------------

CEMENTING_PROGRAM_MD = r"""
# CEMENTING JOB PROGRAM — {{job_type}} — {{well_name}}

**Field:** {{field_name}} | **Rig/Unit:** {{rig_name}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Perform {{job_type}} for well **{{well_name}}**:

- Interval: {{interval}}
- Slurry: {{slurry_type}} ({{slurry_density}} ppg)
- Target: {{job_objective}}

## 2. PRE-JOB DATA

| Item | Value |
|---|---|
| Well | {{well_name}} |
| Job Type | {{job_type}} |
| Interval | {{interval}} |
| Hole / Casing Size | {{hole_size}} |
| String / Tubing Size | {{string_size}} |
| Shoe / Setting Depth | {{setting_depth}} m |
| Planned TOC | {{toc}} m |
| Slurry Type | {{slurry_type}} |
| Slurry Density | {{slurry_density}} ppg |
| Slurry Volume | {{slurry_volume}} bbl |
| Mix Water | {{mix_water}} bbl |
| Displacement Volume | {{displacement_volume}} bbl |
| Displacement Rate | {{displacement_rate}} bpm |
| Max Surface Pressure | {{max_pressure}} psi |
| WOC Time | {{woc_time}} hrs |
| Plug Bump Pressure | {{plug_bump}} psi |

## 3. CEMENT SLURRY DESIGN

- **Lead slurry:** {{lead_slurry}} — density {{lead_density}} ppg,
  yield {{lead_yield}} ft³/sk, thickening time {{lead_tt}} hrs.
- **Tail slurry:** {{tail_slurry}} — density {{tail_density}} ppg,
  yield {{tail_yield}} ft³/sk, thickening time {{tail_tt}} hrs.
- **Additives:** {{additives}}.
- **Spacer:** {{spacer}} ({{spacer_volume}} bbl) — density {{spacer_density}} ppg.
- **Wash:** {{wash}} ({{wash_volume}} bbl).
- Lab test results attached; slurry approved by {{slurry_approved}}.

### Volume Calculation Summary

| Component | Volume (bbl) |
|---|---|
| Annular volume (with {{excess}}% excess) | {{annular_volume}} |
| Lead slurry | {{lead_volume}} |
| Tail slurry | {{tail_volume}} |
| Spacer | {{spacer_volume}} |
| Wash | {{wash_volume}} |
| Displacement | {{displacement_volume}} |

## 4. EQUIPMENT & MATERIALS

| Item | Specification | Qty | Status |
|---|---|---|---|
| Cement unit | {{cement_unit}} | 1 | |
| Bulk cement | {{bulk_cement}} | | |
| Mix water tanks | | | |
| Cement head | {{cement_head}} | 1 | |
| Plug set (top/bottom) | {{plug_set}} | 1 | |
| Hoses & lines | tested to {{line_test}} psi | | |
| Float equipment | {{float_equipment}} | | |

## 5. EXECUTION PROCEDURE

### 5.1 Preparation

1. Rig up cement unit and lines; pressure test to {{line_test}} psi.
2. Verify float equipment and shoe track ({{shoe_track}} m).
3. Mix and test slurry per lab; record density continuously.
4. Circulate hole/well at {{circulation_rate}} bpm until clean
   (minimum {{circulation_time}}).
5. Hold pre-job meeting; confirm volumes and rates with all parties.

### 5.2 Job Execution

1. Pump {{wash_volume}} bbl wash at {{displacement_rate}} bpm.
2. Pump {{spacer_volume}} bbl spacer ({{spacer_density}} ppg).
3. Drop bottom plug; pump lead slurry {{lead_volume}} bbl
   (rate {{lead_rate}} bpm).
4. Drop top plug (if applicable); pump tail slurry {{tail_volume}} bbl
   (rate {{tail_rate}} bpm).
5. Displace with {{displacement_volume}} bbl at {{displacement_rate}} bpm.
6. Bump plug at {{plug_bump}} psi; hold {{plug_hold}} psi and check
   backflow.
7. Bleed; check float; record final volumes.

### 5.3 Post-Job

1. WOC {{woc_time}} hrs.
2. Pressure test shoe: {{shoe_test}} psi, 15 min.
3. Tag TOC ({{toc}} m) if required.
4. CBL/VDL where required ({{cbl_required}}).
5. Complete cement job report.

## 6. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Preparation | Lines tested; slurry lab test accepted |
| HP-02 | Job | Plug bumped; no backflow |
| HP-03 | Post | Shoe test accepted |

## 7. CONTINGENCIES

- **Lost circulation during job:** reduce rate, continue with plan if
  returns partial; if total losses — stop, evaluate, secondary job.
- **Premature set:** pull out of interval, circulate; inform office.
- **Plug not bumped:** verify displacement volume; do not over-displace
  beyond calculated + tolerance.
- **No float back:** leave pressure on; WOC longer; tag and test.

## 8. HSE

- High-pressure work — barricade zone, tested lines, communication.
- Chemical handling per SDS; PPE mandatory.
- No personnel in line of fire during plug bump.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
"""

CEMENTING_PROGRAM = TemplateDef(
    key="cementing_program",
    name="Cementing Job Program",
    icon="🧱",
    kind="Program",
    description=(
        "Single cementing job program: slurry design, volume summary, "
        "equipment, step-by-step execution, hold points and contingencies "
        "(casing / plug / squeeze)."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  group="Job"),
        InputSpec("field_name", "Field", "text", group="Job"),
        InputSpec("rig_name", "Rig / Unit", "text", group="Job"),
        InputSpec("job_type", "Job Type", "combo",
                  options=["Primary casing cementing", "Cement plug",
                           "Squeeze cementing", "Liner cementing",
                           "Liner top / tie-back"],
                  group="Job"),
        InputSpec("job_objective", "Job Objective", "textarea",
                  placeholder="e.g. isolate zone, provide shoe integrity",
                  group="Job"),
        InputSpec("interval", "Interval", "text", group="Job"),
        InputSpec("hole_size", "Hole / Casing Size", "text",
                  placeholder="e.g. 12-1/4\" hole / 9-5/8\" casing",
                  group="Job"),
        InputSpec("string_size", "String / Tubing Size", "text",
                  placeholder="e.g. 3-1/2\" DP", group="Job"),
        InputSpec("setting_depth", "Setting Depth", "number", unit="m",
                  group="Job"),
        InputSpec("toc", "Planned TOC", "number", unit="m", group="Job"),
        InputSpec("shoe_track", "Shoe Track Length", "number", unit="m",
                  default="30", group="Job"),
        InputSpec("slurry_type", "Slurry Type", "combo",
                  options=["Class G 15.8 ppg", "Class G + silica 16.4 ppg",
                           "Class H 16.0 ppg", "Lightweight 12.5-13.5 ppg",
                           "Foam cement", "Micro-cement"],
                  group="Slurry"),
        InputSpec("slurry_density", "Slurry Density", "number", unit="ppg",
                  group="Slurry"),
        InputSpec("slurry_volume", "Slurry Volume", "number", unit="bbl",
                  group="Slurry"),
        InputSpec("lead_slurry", "Lead Slurry", "text", group="Slurry"),
        InputSpec("lead_density", "Lead Density", "number", unit="ppg",
                  group="Slurry"),
        InputSpec("lead_yield", "Lead Yield", "number", unit="ft³/sk",
                  group="Slurry"),
        InputSpec("lead_tt", "Lead Thickening Time", "number", unit="hrs",
                  group="Slurry"),
        InputSpec("lead_volume", "Lead Volume", "number", unit="bbl",
                  group="Slurry"),
        InputSpec("tail_slurry", "Tail Slurry", "text", group="Slurry"),
        InputSpec("tail_density", "Tail Density", "number", unit="ppg",
                  group="Slurry"),
        InputSpec("tail_yield", "Tail Yield", "number", unit="ft³/sk",
                  group="Slurry"),
        InputSpec("tail_tt", "Tail Thickening Time", "number", unit="hrs",
                  group="Slurry"),
        InputSpec("tail_volume", "Tail Volume", "number", unit="bbl",
                  group="Slurry"),
        InputSpec("additives", "Additives", "textarea",
                  placeholder="e.g. retarder, fluid loss, dispersant",
                  group="Slurry"),
        InputSpec("spacer", "Spacer Type", "text", group="Fluids"),
        InputSpec("spacer_density", "Spacer Density", "number", unit="ppg",
                  group="Fluids"),
        InputSpec("spacer_volume", "Spacer Volume", "number", unit="bbl",
                  group="Fluids"),
        InputSpec("wash", "Wash Type", "text", default="Fresh water",
                  group="Fluids"),
        InputSpec("wash_volume", "Wash Volume", "number", unit="bbl",
                  group="Fluids"),
        InputSpec("mix_water", "Mix Water Volume", "number", unit="bbl",
                  group="Fluids"),
        InputSpec("displacement_volume", "Displacement Volume", "number",
                  unit="bbl", group="Fluids"),
        InputSpec("displacement_rate", "Displacement Rate", "number",
                  unit="bpm", group="Fluids"),
        InputSpec("annular_volume", "Annular Volume", "number", unit="bbl",
                  group="Volumes"),
        InputSpec("excess", "Excess", "number", unit="%", default="50",
                  group="Volumes"),
        InputSpec("lead_rate", "Lead Pump Rate", "number", unit="bpm",
                  default="6", group="Execution"),
        InputSpec("tail_rate", "Tail Pump Rate", "number", unit="bpm",
                  default="4", group="Execution"),
        InputSpec("circulation_rate", "Circulation Rate", "number", unit="bpm",
                  default="8", group="Execution"),
        InputSpec("circulation_time", "Circulation Time", "number", unit="hrs",
                  default="2", group="Execution"),
        InputSpec("max_pressure", "Max Surface Pressure", "number", unit="psi",
                  group="Execution"),
        InputSpec("plug_bump", "Plug Bump Pressure", "number", unit="psi",
                  default="800", group="Execution"),
        InputSpec("plug_hold", "Hold Pressure After Bump", "number", unit="psi",
                  default="500", group="Execution"),
        InputSpec("woc_time", "WOC Time", "number", unit="hrs", default="12",
                  group="Post-Job"),
        InputSpec("shoe_test", "Shoe Test Pressure", "number", unit="psi",
                  default="2500", group="Post-Job"),
        InputSpec("cbl_required", "CBL/VDL Required", "combo",
                  options=["YES", "NO"], group="Post-Job"),
        InputSpec("cement_unit", "Cement Unit", "text",
                  placeholder="e.g. twin pump 600 HP", group="Equipment"),
        InputSpec("bulk_cement", "Bulk Cement", "text",
                  placeholder="e.g. 400 sk Class G", group="Equipment"),
        InputSpec("cement_head", "Cement Head", "text",
                  placeholder="e.g. 5K quick release", group="Equipment"),
        InputSpec("plug_set", "Plug Set", "text",
                  placeholder="e.g. top/bottom wiper plugs",
                  group="Equipment"),
        InputSpec("float_equipment", "Float Equipment", "text",
                  placeholder="e.g. float collar + float shoe",
                  group="Equipment"),
        InputSpec("line_test", "Line Test Pressure", "number", unit="psi",
                  default="5000", group="Equipment"),
        InputSpec("slurry_approved", "Slurry Approved By", "text",
                  group="Equipment"),
    ],
    markdown=CEMENTING_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 7. WELL TESTING PROGRAM
# ----------------------------------------------------------------------------

WELL_TESTING_PROGRAM_MD = r"""
# WELL TESTING PROGRAM — {{well_name}}

**Field:** {{field_name}} | **Rig/Unit:** {{rig_name}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Test well **{{well_name}}** to:

- Confirm flow potential and reservoir parameters
  (permeability, skin, pressure, temperature).
- Obtain fluid samples ({{samples}}).
- Establish deliverability on {{chokes}} chokes.
- {{test_purpose}}

## 2. TEST DESIGN

| Parameter | Value |
|---|---|
| Well | {{well_name}} |
| Test Type | {{test_type}} |
| Interval | {{interval}} |
| Expected Rate | {{expected_rate}} |
| Expected WHP | {{expected_whp}} psi |
| Flowing Temperature | {{flow_temp}} °F |
| H2S / CO2 | {{h2s}} / {{co2}} |
| Choke Sizes | {{chokes}} |
| Test Duration (min) | {{test_duration}} hrs |
| Max Surface Pressure (test equipment) | {{test_wp}} psi |

## 3. EQUIPMENT SETUP

| Item | Specification | Qty |
|---|---|---|
| Test string (DST tools) | {{dst_tools}} | 1 |
| Subsea test tree / surface test tree | {{stt}} | 1 |
| Choke manifold | {{choke_manifold}} | 1 |
| Separator | {{separator}} | 1 |
| Heater | {{heater}} | 1 |
| Burner / flare | {{burner}} | 1 |
| Tanks | {{tanks}} | |
| ESD system | | 1 |
| Sampling equipment | | |

- All equipment pressure tested to {{test_wp}} psi (hold 15 min) before
  flowing.
- ESD function tested; emergency shutdown and alarm tested with crew.

## 4. EXECUTION PROCEDURE

### 4.1 Preparations

1. Rig up and pressure test all surface equipment ({{test_wp}} psi).
2. Function test ESD, valves, and communications.
3. Verify H2S monitoring and flare/burner readiness ({{h2s}}).

### 4.2 Test Sequence

1. RIH test string to {{interval}}; set packer; function test tools.
2. Perforate / open SSD as per plan: {{opening_method}}.
3. Flow through {{chokes}} chokes in sequence.
4. Record per period: WHP, WHT, rate, BS&W, gas rate, H2S, annulus pressure.
5. Shut-in for pressure build-up: {{bu_duration}} hrs.
6. POOH test string; rig down.

### 4.3 Sampling

- Oil: {{oil_samples}} — API gravity, BS&W, composition.
- Gas: {{gas_samples}} — composition, H2S/CO2, SG.
- Water: {{water_samples}} — salinity, ions.
- PVT samples where required.

## 5. DATA RECORDING

| Period | Choke | Rate | WHP | WHT | BS&W | GOR | H2S | Remarks |
|---|---|---|---|---|---|---|---|---|

## 6. HSE

- Flare/burner operations: permit, wind monitoring, no-fly zone.
- H2S: continuous monitoring, BA/SCBA, wind sock, alarms at
  {{h2s_alarm}} ppm.
- No smoking in test area; certified electrical equipment in Zone 1.

## 7. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Setup | Equipment tested; ESD functional |
| HP-02 | Flow | First flow results reviewed |
| HP-03 | Build-up | BU complete; data accepted |

## 8. REPORT

- Final well test report with interpretation (deliverability, kh, skin)
  delivered within {{report_days}} days.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
"""

WELL_TESTING_PROGRAM = TemplateDef(
    key="well_testing_program",
    name="Well Testing Program",
    icon="📊",
    kind="Program",
    description=(
        "Well test / DST program: test design, equipment setup, flow "
        "sequence, sampling, data recording and HSE."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  group="Test"),
        InputSpec("field_name", "Field", "text", group="Test"),
        InputSpec("rig_name", "Rig / Unit", "text", group="Test"),
        InputSpec("test_type", "Test Type", "combo",
                  options=["DST (Drill Stem Test)", "Production Test",
                           "Flow after completion", "Injectivity Test",
                           "Build-up / Drawdown"],
                  group="Test"),
        InputSpec("test_purpose", "Purpose", "textarea",
                  placeholder="e.g. confirm commercial flow",
                  group="Test"),
        InputSpec("interval", "Interval", "text",
                  placeholder="e.g. 2450-2480 m MD", group="Test"),
        InputSpec("expected_rate", "Expected Rate", "text",
                  placeholder="e.g. 1500 bopd", group="Test"),
        InputSpec("expected_whp", "Expected WHP", "number", unit="psi",
                  group="Test"),
        InputSpec("flow_temp", "Flowing Temperature", "number", unit="°F",
                  group="Test"),
        InputSpec("h2s", "H2S", "text", placeholder="e.g. 300 ppm",
                  group="Test"),
        InputSpec("co2", "CO2", "text", group="Test"),
        InputSpec("chokes", "Choke Sizes", "text", placeholder="e.g. 24/64, 32/64, 40/64",
                  group="Test"),
        InputSpec("test_duration", "Test Duration", "number", unit="hrs",
                  default="48", group="Test"),
        InputSpec("bu_duration", "Build-up Duration", "number", unit="hrs",
                  default="24", group="Test"),
        InputSpec("test_wp", "Test Equipment WP", "number", unit="psi",
                  default="10000", group="Equipment"),
        InputSpec("dst_tools", "DST Tools", "text",
                  placeholder="e.g. RTTS packer + tester valve + gauges",
                  group="Equipment"),
        InputSpec("stt", "Surface Test Tree", "text",
                  placeholder="e.g. 4-1/16\" 10K", group="Equipment"),
        InputSpec("choke_manifold", "Choke Manifold", "text",
                  placeholder="e.g. 10K, 2 chokes", group="Equipment"),
        InputSpec("separator", "Separator", "text",
                  placeholder="e.g. 3-phase 1440 psi", group="Equipment"),
        InputSpec("heater", "Heater", "text", group="Equipment"),
        InputSpec("burner", "Burner / Flare", "text", group="Equipment"),
        InputSpec("tanks", "Tanks", "text", placeholder="e.g. 3 x 500 bbl",
                  group="Equipment"),
        InputSpec("opening_method", "Opening Method", "combo",
                  options=["Perforation (wireline)", "Open SSD",
                           "Tubing conveyed perforation"],
                  group="Execution"),
        InputSpec("oil_samples", "Oil Samples", "text",
                  placeholder="e.g. 4 x surface + 2 PVT", group="Samples"),
        InputSpec("gas_samples", "Gas Samples", "text", group="Samples"),
        InputSpec("water_samples", "Water Samples", "text", group="Samples"),
        InputSpec("samples", "Samples Summary", "text", group="Samples"),
        InputSpec("h2s_alarm", "H2S Alarm Level", "number", unit="ppm",
                  default="10", group="HSE"),
        InputSpec("report_days", "Report Delivery", "number", unit="days",
                  default="14", group="HSE"),
    ],
    markdown=WELL_TESTING_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 8. FISHING PROGRAM
# ----------------------------------------------------------------------------

FISHING_PROGRAM_MD = r"""
# FISHING OPERATION PROGRAM — {{well_name}}

**Field:** {{field_name}} | **Rig/Unit:** {{rig_name}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Recover the fish in well **{{well_name}}**:

- **Fish description:** {{fish_description}}
- **Fish top depth:** {{fish_top}} m
- **Fish length:** {{fish_length}} m
- **Condition:** {{fish_condition}}
- **Previous attempts:** {{previous_attempts}}

## 2. FISH DATA & WELL CONDITIONS

| Item | Value |
|---|---|
| Well | {{well_name}} |
| Fish | {{fish_description}} |
| Fish Top | {{fish_top}} m |
| Fish Length | {{fish_length}} m |
| Fish OD / ID | {{fish_od}} / {{fish_id}} |
| Fishing Neck / Catch Profile | {{fish_neck}} |
| Hole / Casing Size | {{hole_size}} |
| Mud Weight | {{mud_weight}} ppg |
| Open Hole / Cased Hole | {{open_hole}} |
| H2S | {{h2s}} |

## 3. FISHING STRATEGY

**Primary method:** {{primary_method}}

1. {{primary_steps}}

**Secondary method:** {{secondary_method}}

1. {{secondary_steps}}

## 4. FISHING EQUIPMENT

| Item | Specification | Qty |
|---|---|---|
| Fishing tool #1 | {{tool1}} | 1+1 |
| Fishing tool #2 | {{tool2}} | 1 |
| Jars | {{jars}} | 1 |
| Intensifier | {{intensifier}} | 1 |
| String ({{string_size}}) | washed/drifted | |
| Shock tool | {{shock_tool}} | 1 |

## 5. PROCEDURE

### 5.1 Preparations

1. Wash, drift and measure all fishing string components.
2. Function test jars and fishing tools at surface.
3. Verify fish depth with drift/gauge run ({{gauge_run}}).
4. Pre-job meeting; agree pull limits and contingency with all parties.

### 5.2 Run In Hole

1. RIH fishing assembly slowly; fill string every {{fill_interval}} stands.
2. Approach fish top cautiously (< {{approach_speed}} m/min).
3. Tag fish; confirm depth; slack off to engage ({{engage_weight}} klbs).

### 5.3 Engage & Pull

1. Jar as per plan: {{jarring_plan}}.
2. Work pipe: overpull up to {{max_overpull}} klbs, slack-off
   {{max_slackoff}} klbs.
3. If free: POOH carefully; inspect fish at surface.
4. If not free after {{attempt_limit}} attempts: apply secondary method
   ({{secondary_method}}) or POOH and re-plan.

### 5.4 POOH

1. POOH with fish; no rotation; monitor overpull.
2. Lay down fish; inspect; preserve for investigation.

## 6. CONTINGENCIES

- **Tool parts in hole:** go to fishing tool #2 / magnet / junk basket.
- **Stuck fishing string:** back-off at safety joint, continue with
  contingency plan.
- **Lost circulation:** treat before continuing ({{lc_plan}}).
- **H2S:** stop if H2S above action level; activate emergency plan.

## 7. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Prep | Fishing tools function tested |
| HP-02 | Engage | Fish tagged and engaged — confirm with Company |
| HP-03 | Pull | Fish recovered / decision to abandon fishing |

## 8. HSE

- Dropped object prevention; barricade around well center.
- Crane and lifting plan for heavy fish.
- Communication between driller and supervisor at all times.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
"""

FISHING_PROGRAM = TemplateDef(
    key="fishing_program",
    name="Fishing Operation Program",
    icon="🎣",
    kind="Program",
    description=(
        "Fishing operation program: fish data, strategy, equipment, "
        "step-by-step engagement and pull, contingencies."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  group="Fish"),
        InputSpec("field_name", "Field", "text", group="Fish"),
        InputSpec("rig_name", "Rig / Unit", "text", group="Fish"),
        InputSpec("fish_description", "Fish Description", "textarea",
                  placeholder="e.g. 3-1/2\" DP + BHA (mud motor + bit)",
                  required=True, group="Fish"),
        InputSpec("fish_top", "Fish Top Depth", "number", unit="m",
                  group="Fish"),
        InputSpec("fish_length", "Fish Length", "number", unit="m",
                  group="Fish"),
        InputSpec("fish_condition", "Fish Condition", "textarea",
                  placeholder="e.g. stuck, damaged box, key-seated",
                  group="Fish"),
        InputSpec("previous_attempts", "Previous Attempts", "textarea",
                  placeholder="e.g. 1 x overshot — jarred 4 hrs",
                  group="Fish"),
        InputSpec("fish_od", "Fish OD", "number", unit="in", group="Fish"),
        InputSpec("fish_id", "Fish ID", "number", unit="in", group="Fish"),
        InputSpec("fish_neck", "Catch Profile", "text",
                  placeholder="e.g. 3-1/2\" IF box / 6-1/4\" packer mandrel",
                  group="Fish"),
        InputSpec("hole_size", "Hole / Casing Size", "text",
                  group="Well Conditions"),
        InputSpec("mud_weight", "Mud Weight", "number", unit="ppg",
                  group="Well Conditions"),
        InputSpec("open_hole", "Open / Cased Hole", "combo",
                  options=["Cased hole", "Open hole"], group="Well Conditions"),
        InputSpec("h2s", "H2S", "combo", options=["NO", "YES"],
                  group="Well Conditions"),
        InputSpec("primary_method", "Primary Method", "combo",
                  options=["Overshot + jarring", "Spear", "Taper tap",
                           "Die collar", "Magnet / junk basket",
                           "Washover"], group="Strategy"),
        InputSpec("primary_steps", "Primary Method Steps", "textarea",
                  group="Strategy"),
        InputSpec("secondary_method", "Secondary Method", "combo",
                  options=["Washover", "Free-point + back-off", "Cutting",
                           "Milling", "Chemical cutter", "CT fishing"],
                  group="Strategy"),
        InputSpec("secondary_steps", "Secondary Method Steps", "textarea",
                  group="Strategy"),
        InputSpec("tool1", "Primary Fishing Tool", "text",
                  placeholder="e.g. 7-3/4\" overshot w/ grapple",
                  group="Equipment"),
        InputSpec("tool2", "Secondary Fishing Tool", "text", group="Equipment"),
        InputSpec("jars", "Jars", "text", placeholder="e.g. 6-1/2\" drilling jar",
                  group="Equipment"),
        InputSpec("intensifier", "Intensifier / Accelerator", "text",
                  group="Equipment"),
        InputSpec("shock_tool", "Shock Tool", "text", group="Equipment"),
        InputSpec("string_size", "String Size", "text", default="3-1/2\" DP",
                  group="Equipment"),
        InputSpec("gauge_run", "Gauge / Drift Run Required", "combo",
                  options=["YES", "NO"], group="Equipment"),
        InputSpec("fill_interval", "Fill Up Interval", "number", unit="stands",
                  default="10", group="Execution"),
        InputSpec("approach_speed", "Approach Speed", "number", unit="m/min",
                  default="5", group="Execution"),
        InputSpec("engage_weight", "Engage Weight", "number", unit="klbs",
                  group="Execution"),
        InputSpec("max_overpull", "Max Overpull", "number", unit="klbs",
                  group="Execution"),
        InputSpec("max_slackoff", "Max Slack-off", "number", unit="klbs",
                  group="Execution"),
        InputSpec("jarring_plan", "Jarring Plan", "textarea",
                  placeholder="e.g. up-jar 20k x 30 min, rest 15 min",
                  group="Execution"),
        InputSpec("attempt_limit", "Attempt Limit", "number", unit="hrs",
                  default="8", group="Execution"),
        InputSpec("lc_plan", "Lost Circulation Plan", "text",
                  placeholder="e.g. LCM pill 50 bbl @ 80 ppb", group="HSE"),
    ],
    markdown=FISHING_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 9. STIMULATION PROGRAM
# ----------------------------------------------------------------------------

STIMULATION_PROGRAM_MD = r"""
# WELL STIMULATION PROGRAM — {{stim_type}} — {{well_name}}

**Field:** {{field_name}} | **Rig/Unit:** {{rig_name}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Stimulate well **{{well_name}}** by **{{stim_type}}** over interval
**{{interval}}** to {{stim_objective}}.

## 2. DESIGN SUMMARY

| Parameter | Value |
|---|---|
| Well | {{well_name}} |
| Stimulation Type | {{stim_type}} |
| Interval | {{interval}} |
| Treatment Fluid | {{treatment_fluid}} |
| Pad Volume | {{pad_volume}} bbl |
| Main Treatment Volume | {{treatment_volume}} bbl |
| Flush Volume | {{flush_volume}} bbl |
| Pump Rate (planned) | {{pump_rate}} bpm |
| Max Surface Pressure | {{max_pressure}} psi |
| Breakdown Pressure (expected) | {{breakdown_pressure}} psi |
| Proppant (if frac) | {{proppant}} |
| H2S | {{h2s}} |

## 3. FLUID & CHEMICALS

- Base fluid: {{base_fluid}} ({{base_fluid_volume}} bbl).
- Additives: {{additives}}.
- Quality control: samples taken per stage; lab tests per program
  ({{fluid_tests}}).
- Compatibility test with formation fluid: {{compatibility}}.

## 4. EQUIPMENT

| Item | Specification | Qty |
|---|---|---|
| Pump unit | {{pump_unit}} | 2 |
| Blender | {{blender}} | 1 |
| Acid / chemical tanks | {{acid_tanks}} | |
| High-pressure iron | tested to {{line_test}} psi | |
| Choke manifold / returns | {{returns_manifold}} | |
| Nitrogen unit (if used) | {{nitrogen}} | |
| Data van | | 1 |

## 5. EXECUTION PROCEDURE

### 5.1 Preparation

1. Rig up equipment; pressure test lines to {{line_test}} psi.
2. Verify well integrity: {{well_integrity}}.
3. Confirm interval open and fluid level ({{fluid_level}}).
4. Pre-job meeting with all parties; agree communication and H2S watch.

### 5.2 Injection / Breakdown

1. Inject brine/test fluid at low rate ({{inject_rate}} bpm) to confirm
   injectivity ({{injectivity}} bpm @ {{inject_pressure}} psi).
2. Pump pad {{pad_volume}} bbl at {{pump_rate}} bpm.
3. Monitor pressure; note breakdown ({{breakdown_pressure}} psi).

### 5.3 Main Treatment

1. Pump main treatment {{treatment_volume}} bbl at {{pump_rate}} bpm
   (max {{max_pressure}} psi).
2. For fracturing: ramp proppant per schedule
   ({{proppant_schedule}}).
3. Flush with {{flush_volume}} bbl at {{flush_rate}} bpm.
4. Shut in for reaction/leak-off: {{shut_in_time}} min.

### 5.4 Flowback

1. Flow back through {{returns_manifold}} at controlled rate.
2. Collect samples; monitor H2S ({{h2s}}).
3. Record total recovered volume: {{recovered_volume}}.

## 6. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Prep | Equipment tested; fluid QC accepted |
| HP-02 | Breakdown | Injectivity accepted |
| HP-03 | Treatment | Treatment completed per design |
| HP-04 | Flowback | Flowback results reviewed |

## 7. CONTINGENCIES

- **No injectivity:** acid pre-flush / lower rate / reperforate.
- **Pressure above max:** stop, bleed, evaluate, revise program.
- **Surface leak:** shut down, depressurize, repair, re-test.
- **Screen-out (frac):** flush immediately per plan; record final pressure.

## 8. HSE

- Acids/chemicals: SDS, PPE, eye wash, containment.
- High-pressure zone barricaded; remote-controlled valves.
- H2S monitoring {{h2s}} during flowback.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
"""

STIMULATION_PROGRAM = TemplateDef(
    key="stimulation_program",
    name="Stimulation Program (Acid / Frac)",
    icon="💥",
    kind="Program",
    description=(
        "Matrix acidizing or hydraulic fracturing program: design summary, "
        "fluids, equipment, injection/breakdown/treatment/flowback steps."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  group="Stim"),
        InputSpec("field_name", "Field", "text", group="Stim"),
        InputSpec("rig_name", "Rig / Unit", "text", group="Stim"),
        InputSpec("stim_type", "Stimulation Type", "combo",
                  options=["Matrix acidizing", "Acid fracturing",
                           "Hydraulic fracturing (proppant)",
                           "Scale squeeze", "Sandstone acid"],
                  group="Stim"),
        InputSpec("stim_objective", "Objective", "textarea",
                  placeholder="e.g. remove near-wellbore damage, enhance kh",
                  group="Stim"),
        InputSpec("interval", "Interval", "text", group="Stim"),
        InputSpec("treatment_fluid", "Treatment Fluid", "text",
                  placeholder="e.g. 15% HCl + additives", group="Design"),
        InputSpec("pad_volume", "Pad Volume", "number", unit="bbl",
                  group="Design"),
        InputSpec("treatment_volume", "Main Treatment Volume", "number",
                  unit="bbl", group="Design"),
        InputSpec("flush_volume", "Flush Volume", "number", unit="bbl",
                  group="Design"),
        InputSpec("pump_rate", "Pump Rate", "number", unit="bpm",
                  group="Design"),
        InputSpec("flush_rate", "Flush Rate", "number", unit="bpm",
                  group="Design"),
        InputSpec("max_pressure", "Max Surface Pressure", "number", unit="psi",
                  group="Design"),
        InputSpec("breakdown_pressure", "Expected Breakdown", "number",
                  unit="psi", group="Design"),
        InputSpec("proppant", "Proppant", "text",
                  placeholder="e.g. 20/40 ISP 150,000 lbs", group="Design"),
        InputSpec("proppant_schedule", "Proppant Ramp Schedule", "textarea",
                  group="Design"),
        InputSpec("base_fluid", "Base Fluid", "text", default="Fresh water",
                  group="Fluids"),
        InputSpec("base_fluid_volume", "Base Fluid Volume", "number",
                  unit="bbl", group="Fluids"),
        InputSpec("additives", "Additives", "textarea",
                  placeholder="e.g. corrosion inhibitor, iron control, surfactant",
                  group="Fluids"),
        InputSpec("fluid_tests", "Fluid QC Tests", "text",
                  placeholder="e.g. acid strength, emulsion test",
                  group="Fluids"),
        InputSpec("compatibility", "Compatibility Test", "combo",
                  options=["OK", "Pending", "Not required"],
                  group="Fluids"),
        InputSpec("pump_unit", "Pump Unit", "text",
                  placeholder="e.g. 2000 HP frac pump", group="Equipment"),
        InputSpec("blender", "Blender", "text", group="Equipment"),
        InputSpec("acid_tanks", "Acid / Chemical Tanks", "text",
                  placeholder="e.g. 2 x 500 bbl lined", group="Equipment"),
        InputSpec("returns_manifold", "Returns Manifold", "text",
                  placeholder="e.g. 5K choke manifold to tanks",
                  group="Equipment"),
        InputSpec("nitrogen", "Nitrogen Unit", "text",
                  placeholder="e.g. 2 x 120,000 SCFN", group="Equipment"),
        InputSpec("line_test", "Line Test Pressure", "number", unit="psi",
                  default="5000", group="Equipment"),
        InputSpec("well_integrity", "Well Integrity Check", "textarea",
                  placeholder="e.g. annulus pressure tested, no leaks",
                  group="Execution"),
        InputSpec("fluid_level", "Fluid Level", "text",
                  placeholder="e.g. full to surface", group="Execution"),
        InputSpec("inject_rate", "Initial Inject Rate", "number", unit="bpm",
                  group="Execution"),
        InputSpec("injectivity", "Injectivity", "text",
                  placeholder="e.g. 5 bpm @ 1500 psi", group="Execution"),
        InputSpec("inject_pressure", "Inject Pressure", "number", unit="psi",
                  group="Execution"),
        InputSpec("shut_in_time", "Shut-in Time", "number", unit="min",
                  default="30", group="Execution"),
        InputSpec("recovered_volume", "Recovered Volume", "text",
                  placeholder="e.g. 70% of pumped", group="Execution"),
        InputSpec("h2s", "H2S Present", "combo", options=["NO", "YES"],
                  group="HSE"),
    ],
    markdown=STIMULATION_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 10. COILED TUBING PROGRAM
# ----------------------------------------------------------------------------

COILED_TUBING_PROGRAM_MD = r"""
# COILED TUBING OPERATION PROGRAM — {{ct_operation}} — {{well_name}}

**Field:** {{field_name}} | **Unit:** {{ct_unit}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Perform **{{ct_operation}}** in well **{{well_name}}** using coiled tubing:

- Target depth: {{target_depth}} m
- Well fluid / pressure: {{well_conditions}}
- H2S: {{h2s}}

## 2. OPERATION DATA

| Parameter | Value |
|---|---|
| Well | {{well_name}} |
| CT Operation | {{ct_operation}} |
| CT Size | {{ct_size}} |
| CT Length Available | {{ct_length}} m |
| Target Depth | {{target_depth}} m |
| Max Annulus Pressure | {{max_annulus_pressure}} psi |
| Max CT Pressure | {{max_ct_pressure}} psi |
| Working Fluid | {{working_fluid}} |
| Pump Rate | {{pump_rate}} bpm |
| Max Pull | {{max_pull}} lbs |
| BHA | {{bha}} |

## 3. EQUIPMENT

| Item | Specification | Qty |
|---|---|---|
| CT unit | {{ct_unit}} | 1 |
| Injector head | {{injector}} | 1 |
| Stripper / BOP stack | {{ct_bop}} | 1 |
| Power pack | | 1 |
| Control cabin | | 1 |
| Pump | {{pump}} | 1 |
| Nitrogen (if used) | {{nitrogen}} | |

- CT string inspected per API 5C7; last inspection date: {{ct_inspection}}.
- BOP stack tested to {{bop_test}} psi before operations.

## 4. PROCEDURE

### 4.1 Preparation

1. Rig up CT unit; pressure test lines and BOP stack
   ({{bop_test}} psi).
2. Verify wellhead access and lubricator/riser ({{riser}}).
3. Confirm CT string fatigue log within limits.
4. Pre-job meeting; agree parameters and emergency response.

### 4.2 Run In Hole

1. RIH CT at {{rih_speed}} m/min max, monitoring weight and pressure.
2. Fill/bleed annulus to maintain control ({{annulus_control}}).
3. Tag depth at {{target_depth}} m; record weights.

### 4.3 Operation

{{operation_steps}}

### 4.4 POOH

1. POOH at controlled speed; monitor returns and pressure.
2. Bleed and verify well static; rig down.

## 5. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Prep | BOP and lines tested |
| HP-02 | RIH | Target depth tagged and confirmed |
| HP-03 | Operation | Operation completed per design |
| HP-04 | POOH | Well static; CT laid down |

## 6. CONTINGENCIES

- **CT stuck:** work within limits, jarring via CT, spotting; back-off /
  chemical cutter as last resort.
- **Leak in CT:** shut down, bleed, evaluate, cut/POOH per procedure.
- **Well kick:** close BOP, circulate per plan; emergency response.
- **Lost circulation:** treat with LCM pills per program.

## 7. HSE

- Red zone management around injector head.
- No personnel under suspended CT.
- H2S monitoring {{h2s}}; gas detection alarms tested.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
"""

COILED_TUBING_PROGRAM = TemplateDef(
    key="coiled_tubing_program",
    name="Coiled Tubing Operation Program",
    icon="🌀",
    kind="Program",
    description=(
        "Coiled tubing operation program: RIH, operation, POOH with BOP "
        "requirements, contingencies and HSE."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  group="CT"),
        InputSpec("field_name", "Field", "text", group="CT"),
        InputSpec("ct_operation", "Operation", "combo",
                  options=["Cleanout / sand bailing", "N2 kick-off",
                           "Scale / wax removal", "Squeeze cementing",
                           "Stimulation (acid/frac)", "Logging",
                           "Perforation", "Fishing", "Plug setting / retrieval"],
                  group="CT"),
        InputSpec("ct_unit", "CT Unit", "text",
                  placeholder="e.g. 2-3/8\" unit, 15,000 ft",
                  group="CT"),
        InputSpec("ct_size", "CT Size", "combo", options=["1-1/4\"", "1-1/2\"",
                  "1-3/4\"", "2\"", "2-3/8\""], group="CT"),
        InputSpec("ct_length", "CT Length Available", "number", unit="m",
                  group="CT"),
        InputSpec("ct_inspection", "Last CT Inspection", "text",
                  placeholder="e.g. 2026-01-15 (API 5C7)", group="CT"),
        InputSpec("target_depth", "Target Depth", "number", unit="m",
                  required=True, group="Well Data"),
        InputSpec("well_conditions", "Well Conditions", "textarea",
                  placeholder="e.g. 8.6 ppg brine, static, 300 psi WHP",
                  group="Well Data"),
        InputSpec("h2s", "H2S", "combo", options=["NO", "YES"],
                  group="Well Data"),
        InputSpec("max_annulus_pressure", "Max Annulus Pressure", "number",
                  unit="psi", group="Well Data"),
        InputSpec("max_ct_pressure", "Max CT Pressure", "number", unit="psi",
                  group="Well Data"),
        InputSpec("working_fluid", "Working Fluid", "text",
                  placeholder="e.g. brine 9.0 ppg / N2", group="Design"),
        InputSpec("pump_rate", "Pump Rate", "number", unit="bpm",
                  group="Design"),
        InputSpec("max_pull", "Max Pull", "number", unit="lbs",
                  group="Design"),
        InputSpec("bha", "BHA", "text",
                  placeholder="e.g. motor + mill / nozzle / gauge cutter",
                  group="Design"),
        InputSpec("operation_steps", "Operation Steps (step by step)",
                  "textarea", required=True,
                  placeholder="1. Pump N2 at 300 scfm...\n2. ...",
                  group="Operation"),
        InputSpec("rih_speed", "RIH Speed (max)", "number", unit="m/min",
                  default="15", group="Operation"),
        InputSpec("annulus_control", "Annulus Control Method", "text",
                  placeholder="e.g. choke manifold, keep 200 psi on annulus",
                  group="Operation"),
        InputSpec("injector", "Injector Head", "text",
                  placeholder="e.g. 80,000 lbs", group="Equipment"),
        InputSpec("ct_bop", "CT BOP Stack", "text",
                  placeholder="e.g. quad stack 15K", group="Equipment"),
        InputSpec("pump", "Pump", "text", placeholder="e.g. 500 HP triplex",
                  group="Equipment"),
        InputSpec("nitrogen", "Nitrogen Unit", "text", group="Equipment"),
        InputSpec("riser", "Lubricator / Riser", "text", group="Equipment"),
        InputSpec("bop_test", "BOP Test Pressure", "number", unit="psi",
                  default="5000", group="Equipment"),
    ],
    markdown=COILED_TUBING_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 11. ADVANCED DRILLING PROGRAM (INTERNATIONAL STANDARD)
# ----------------------------------------------------------------------------
# Flagship template — mirrors the structure of the uploaded real programs
# (S19-type): General Information, Formation Forecast,
# Casing Program & Principles, Directional Design & Trajectory, Mud Program,
# BHA & Bits, Drilling Parameters, Hydraulics, Well Control, Evaluation,
# Completion, Time, Cost, HSE, Hold Points, Contingency, Checklists.
# ----------------------------------------------------------------------------

ADVANCED_DRILLING_PROGRAM_MD = r"""
# DRILLING PROGRAM — {{well_name}} — {{well_classification}}

**Field:** {{field_name}} | **Operator:** {{operator}} | **Contractor:** {{contractor}}
**Rig:** {{rig_name}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## DOCUMENT CONTROL

| Item | Detail |
|---|---|
| Document Title | Drilling Program — {{well_name}} |
| Well | {{well_name}} |
| Field | {{field_name}} |
| Operator | {{operator}} |
| Drilling Contractor | {{contractor}} |
| Rig Name / Number | {{rig_name}} |
| Document Number | {{document_number}} |
| Revision | {{revision}} |
| Classification | {{classification}} |
| Prepared By | {{prepared_by}} |
| Reviewed By | {{reviewed_by}} |
| Approved By | {{approved_by}} |

## TABLE-1 GENERAL INFORMATION

| Parameter | Value |
|---|---|
| Well Name | {{well_name}} |
| Well Classification | {{well_classification}} |
| Well Type | {{well_type}} |
| Well Profile | {{well_profile}} |
| Pad / Platform | {{pad_name}} |
| Country / Province | {{country}} / {{province}} |
| Block / Structure | {{block}} |
| Field | {{field_name}} |
| Ground Elevation | {{ground_elevation}} m |
| Rotary Table Elevation | {{rt_elevation}} m |
| Water Depth (offshore) | {{water_depth}} m |
| Total Depth (MD) | {{td_md}} m |
| Total Depth (TVDss) | {{td_tvd}} m |
| Spud Date | {{spud_date}} |
| Completion Date | {{completion_date}} |
| Reference Well | {{reference_well}} |
| Target Formation | {{target_formation}} |
| Target Zone | {{target_zone}} |
| Reservoir Pressure | {{reservoir_pressure}} psi |
| Reservoir Temperature | {{reservoir_temperature}} °F |
| H2S Content | {{h2s}} |
| CO2 Content | {{co2}} |
| Oil API Gravity | {{api_gravity}} °API |
| Mud Type (reservoir) | {{mud_type}} |
| Completion Type | {{completion_type}} |

## WELL OBJECTIVE

{{well_objective}}

## WELL LOCATION & COORDINATES

| Item | Value |
|---|---|
| Coordinate System | {{coordinate_system}} |
| Wellhead X | {{wh_x}} |
| Wellhead Y | {{wh_y}} |
| Target X | {{target_x}} |
| Target Y | {{target_y}} |
| Wellhead Latitude | {{wh_latitude}} |
| Wellhead Longitude | {{wh_longitude}} |

## TABLE-2 FORMATION FORECAST

{{formations_table}}

> Prognosis based on offset wells {{offset_wells}}; update with actual data.

## TABLE-3 CASING PROGRAM — PRINCIPLE AND PURPOSE

{{casing_table}}

**Design basis:** API RP 5C3 / ISO 10400 — minimum design factors: burst
{{df_burst}}, collapse {{df_collapse}}, tension {{df_tension}}.

| Section | Burst (psi) | Collapse (psi) | Tensile (klbs) | Shoe Test (psi) |
|---|---|---|---|---|
{{casing_ratings_table}}

## DIRECTIONAL PLAN

| Parameter | Value |
|---|---|
| Survey Tool | {{survey_tool}} |
| Survey Interval | {{survey_interval}} m |
| Kickoff Point (KOP) | {{kop}} m MD |
| Build Rate | {{build_rate}} °/30m |
| Hold Inclination | {{hold_inclination}}° |
| Hold Azimuth | {{hold_azimuth}}° |
| Max DLS | {{max_dls}} °/30m |
| Horizontal Displacement | {{horizontal_displacement}} m |
| Anti-Collision Wells | {{anti_collision}} |

### Trajectory (planned)

{{trajectory_table}}

## MUD PROGRAM

{{mud_table}}

**Mud chemicals & additives:** {{mud_chemicals}}

Solids control: {{solids_control}} — mud properties recorded every
30 min while circulating.

## BHA & BITS

{{bha_table}}

### Bit program

| Section | Bit Type | Size (in) | IADC | Manufacturer / Model |
|---|---|---|---|---|
{{bit_table}}

## DRILLING PARAMETERS

| Section | WOB (klbs) | RPM | Flow (GPM) | Max SPP (psi) | Max Torque (ft-lbs) | Overpull (klbs) |
|---|---|---|---|---|---|---|
{{drilling_params_table}}

## HYDRAULICS

| Parameter | Value |
|---|---|
| Annular Velocity (min) | {{ann_velocity}} ft/min |
| Bit Nozzle Velocity | {{nozzle_velocity}} ft/s |
| HSI | {{hsi}} HP/sq.in |
| Max ECD | {{ecd_max}} ppg |
| ROP Target | {{rop_target}} m/hr |

## WELL CONTROL & BOP

- BOP stack: {{bop_stack}} — WP {{bop_wp}} psi.
- BOP test: low {{bop_low_test}} psi / high {{bop_high_test}} psi
  (70% WP), hold 15 min per API RP 53.
- MAASP at shoe: {{maasp}} psi.
- Kick tolerance: {{kick_tolerance}} bbl.
- Slow pump rates: {{slow_pump_rates}}.
- Kill method primary: {{kill_method}}.

## EVALUATION PROGRAM

{{evaluation_table}}

- Coring: {{coring}}
- DST: {{dst}}
- Sampling: {{sampling}}

## COMPLETION SUMMARY

{{completion_type}} — {{completion_summary}}

Key completion data:
- Packer depth: {{packer_depth}} m
- TRSV depth: {{trsv_depth}} m
- SSD depth: {{ssd_depth}} m
- Tubing: {{tubing_string}}

## TIME BREAKDOWN

| Phase | Duration (days) | Cumulative (days) |
|---|---|---|
{{time_table}}

**Total estimated: {{total_days}} days** (incl. {{npt_percent}}% NPT
contingency).

## COST ESTIMATE

{{cost_table}}

**Total estimated cost: {{total_cost}} USD** ({{cost_per_m}} USD/m).

## HSE REQUIREMENTS

- H2S: {{h2s}} — monitoring, BA/SCBA, drills ({{h2s_drills}}).
- Pre-spud HSE audit and safety meeting; permit to work system.
- Emergency response plan; muster and evacuation drills weekly.
- PPE mandatory; TRA for all non-routine operations.
- Waste management per {{waste_plan}}.
- Lifting certificates and equipment inspection valid.

## HOLD POINTS & TEST MATRIX

| HP | Stage | Hold Point | Witness |
|---|---|---|---|
| HP-01 | Pre-spud | BOP tested; rig audit passed | Co. + Client |
| HP-02 | Per section | LOT/FIT accepted; casing & cement confirmed | Co. + Client |
| HP-03 | Drilling out | Shoe test accepted | Co. |
| HP-04 | TD | TD confirmed; evaluation program approved | Co. + Client |
| HP-05 | Completion | Completion confirmed; wellhead tested | Co. + Client |

## CONTINGENCY PLANS

- **Lost circulation:** LCM pills → balanced plug → cement plug; keep hole
  full at all times.
- **Kick:** shut in, strip, circulate per Driller's / W&W method; H2S plan.
- **Stuck pipe:** work/jar within limits, spot pill, back-off, fish.
- **Mud loss with gas:** reduce MW only with pore pressure verification.
- **Weather / equipment failure:** backup equipment list
  ({{backup_equipment}}); winterization {{winterization}}.

## CHECKLISTS

### Pre-Spud Checklist

- [ ] Rig inspected, leveled and certified
- [ ] BOP stack tested and documented
- [ ] Wellhead installed and tested
- [ ] Casing, bits, tools on location and inspected
- [ ] Mud system, chemicals and water tested
- [ ] Surveys / anti-collision approved
- [ ] H2S equipment and BA sets ready
- [ ] Emergency drills completed
- [ ] All services contracted and crews briefed

### Per-Section Checklist

- [ ] Casing tally and running equipment ready
- [ ] Cement lab test approved
- [ ] Torque gauge calibrated
- [ ] Drilling parameters reviewed with crew
- [ ] LOT/FIT equipment ready

## APPENDICES

- Appendix A: Well schematic & casing sketch
- Appendix B: Formation forecast & pore pressure profile
- Appendix C: Directional plan & trajectory tables
- Appendix D: Casing tally & cement volumes
- Appendix E: BOP stack diagram
- Appendix F: Torque tables
- Appendix G: Kill sheet
- Appendix H: Bit records / BHA records
- Appendix I: Daily report & mud report templates
- Appendix J: Cost estimate details

## DOCUMENT APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Reviewed By (Engineering) | {{reviewed_by}} | | |
| Approved By (Operations) | {{approved_by}} | | |
| Approved By (Client) | | | |
"""

ADVANCED_DRILLING_PROGRAM = TemplateDef(
    key="advanced_drilling_program",
    name="Advanced Drilling Program (International Standard)",
    icon="🏆",
    kind="Program",
    description=(
        "The full professional drilling program (international "
        "style, mirrors real field programs): "
        "~75 inputs across 15 groups — general info, formation forecast, "
        "casing program & ratings, directional & trajectory, mud & "
        "chemicals, BHA & bits, parameters, hydraulics, well control, "
        "evaluation, completion, time, cost, HSE, hold points, "
        "contingency and checklists."),
    inputs=[
        # -- Document & Company
        InputSpec("document_number", "Document Number", "text",
                  placeholder="e.g. YAP1-PH1S19-DRDE-PLDR-1001",
                  group="1. Document"),
        InputSpec("classification", "Classification", "combo",
                  options=["Confidential", "Internal", "Restricted", "Public"],
                  group="1. Document"),
        InputSpec("well_name", "Well Name", "text", required=True,
                  placeholder="e.g. S19 / WELL-031", group="1. Document"),
        InputSpec("field_name", "Field", "text", group="1. Document"),
        InputSpec("operator", "Operator", "text", group="1. Document"),
        InputSpec("contractor", "Drilling Contractor", "text", group="1. Document"),
        InputSpec("rig_name", "Rig Name / Number", "text",
                  placeholder="e.g. NIDC Fath 28", group="1. Document"),
        InputSpec("well_classification", "Well Classification", "text",
                  placeholder="e.g. Main reservoir producer (with pilot hole)",
                  group="2. General"),
        InputSpec("well_type", "Well Type", "combo",
                  options=["Development", "Exploration", "Appraisal",
                           "Injection", "Observation", "Sidetrack"],
                  group="2. General"),
        InputSpec("well_profile", "Well Profile", "combo",
                  options=["Vertical", "Directional J-Type",
                           "Directional S-Type", "Horizontal", "ERD",
                           "Pilot hole + horizontal"],
                  group="2. General"),
        InputSpec("pad_name", "Pad / Platform", "text", group="2. General"),
        InputSpec("country", "Country", "text", group="2. General"),
        InputSpec("province", "Province / Region", "text", group="2. General"),
        InputSpec("block", "Block / Structure", "text", group="2. General"),
        InputSpec("reference_well", "Reference Well", "text",
                  placeholder="e.g. SPH-01", group="2. General"),
        InputSpec("spud_date", "Spud Date", "text", group="2. General"),
        InputSpec("completion_date", "Completion Date", "text", group="2. General"),
        InputSpec("ground_elevation", "Ground Elevation", "number", unit="m",
                  group="2. General"),
        InputSpec("rt_elevation", "Rotary Table Elevation", "number",
                  unit="m", group="2. General"),
        InputSpec("water_depth", "Water Depth", "number", unit="m",
                  group="2. General"),
        InputSpec("td_md", "Total Depth (MD)", "number", unit="m",
                  required=True, group="2. General"),
        InputSpec("td_tvd", "Total Depth (TVDss)", "number", unit="m",
                  group="2. General"),
        # -- Location & Target
        InputSpec("coordinate_system", "Coordinate System", "text",
                  default="UTM39N, WGS84", group="3. Location"),
        InputSpec("wh_x", "Wellhead X", "text", group="3. Location"),
        InputSpec("wh_y", "Wellhead Y", "text", group="3. Location"),
        InputSpec("target_x", "Target X", "text", group="3. Location"),
        InputSpec("target_y", "Target Y", "text", group="3. Location"),
        InputSpec("wh_latitude", "Wellhead Latitude", "text", group="3. Location"),
        InputSpec("wh_longitude", "Wellhead Longitude", "text", group="3. Location"),
        # -- Reservoir & Target
        InputSpec("target_formation", "Target Formation", "text",
                  placeholder="e.g. Main reservoir", group="4. Reservoir"),
        InputSpec("target_zone", "Target Zone", "text",
                  placeholder="e.g. Zone 4 (S4)", group="4. Reservoir"),
        InputSpec("reservoir_pressure", "Reservoir Pressure", "number",
                  unit="psi", group="4. Reservoir"),
        InputSpec("reservoir_temperature", "Reservoir Temperature", "number",
                  unit="°F", group="4. Reservoir"),
        InputSpec("h2s", "H2S Content", "text", placeholder="e.g. YES - 3%",
                  group="4. Reservoir"),
        InputSpec("co2", "CO2 Content", "text", placeholder="e.g. 2.6-5.4 mol%",
                  group="4. Reservoir"),
        InputSpec("api_gravity", "Oil API Gravity", "number", unit="°API",
                  group="4. Reservoir"),
        InputSpec("well_objective", "Well Objective", "textarea",
                  placeholder="e.g. Drill pilot hole to base of main "
                  "reservoir, then horizontal hole in the reservoir",
                  group="4. Reservoir"),
        InputSpec("offset_wells", "Offset Wells", "text",
                  placeholder="e.g. S18, S19-B", group="4. Reservoir"),
        # -- Formations & Casing
        InputSpec("formations_table", "Formation Forecast",
                  "table", columns=["Era/System", "Formation", "Lithology",
                                    "MD Top (m)", "MD Bottom (m)",
                                    "PP (ppg)", "FG (ppg)", "Hazard"],
                  group="5. Formations"),
        InputSpec("casing_table", "Casing Program (principle & purpose)",
                  "table", columns=["Section", "Hole (in)", "Depth (m)",
                                    "Casing (in)", "Grade/Wt/Conn",
                                    "Purpose"],
                  required=True, group="5. Formations"),
        InputSpec("casing_ratings_table", "Casing Ratings",
                  "table", columns=["Section", "Burst (psi)", "Collapse (psi)",
                                    "Tensile (klbs)", "Shoe Test (psi)"],
                  group="5. Formations"),
        InputSpec("df_burst", "Min DF Burst", "number", default="1.10",
                  group="5. Formations"),
        InputSpec("df_collapse", "Min DF Collapse", "number", default="1.10",
                  group="5. Formations"),
        InputSpec("df_tension", "Min DF Tension", "number", default="1.60",
                  group="5. Formations"),
        # -- Directional
        InputSpec("survey_tool", "Survey Tool", "combo",
                  options=["MWD", "Gyro MWD", "Gyro While Drilling",
                           "Single Shot", "Multi-Shot", "Gyro + MWD"],
                  group="6. Directional"),
        InputSpec("survey_interval", "Survey Interval", "number", unit="m",
                  default="30", group="6. Directional"),
        InputSpec("kop", "KOP", "number", unit="m MD", group="6. Directional"),
        InputSpec("build_rate", "Build Rate", "number", unit="°/30m",
                  group="6. Directional"),
        InputSpec("hold_inclination", "Hold Inclination", "number", unit="°",
                  group="6. Directional"),
        InputSpec("hold_azimuth", "Hold Azimuth", "number", unit="°",
                  group="6. Directional"),
        InputSpec("max_dls", "Max DLS", "number", unit="°/30m",
                  group="6. Directional"),
        InputSpec("horizontal_displacement", "Horizontal Displacement",
                  "number", unit="m", group="6. Directional"),
        InputSpec("anti_collision", "Anti-Collision Wells", "text",
                  placeholder="e.g. S19-B within 100m — monitor SF > 1.5",
                  group="6. Directional"),
        InputSpec("trajectory_table", "Trajectory Data",
                  "table", columns=["MD (m)", "Incl (°)", "Az (°)", "TVD (m)",
                                    "Closure (m)", "DLS"],
                  group="6. Directional"),
        # -- Mud
        InputSpec("mud_table", "Mud Program per Section",
                  "table", columns=["Section", "Type", "MW in (ppg)",
                                    "MW out (ppg)", "FV (sec)", "PV (cP)",
                                    "YP", "FL (ml)", "Remarks"],
                  group="7. Mud"),
        InputSpec("mud_chemicals", "Mud Chemicals & Additives", "textarea",
                  placeholder="e.g. BARA-WATE, PAC LV-TG, Caustic Soda, "
                  "Bento-Gel API, KCL", group="7. Mud"),
        InputSpec("solids_control", "Solids Control", "text",
                  placeholder="e.g. 4 shakers + desander + centrifuge",
                  group="7. Mud"),
        # -- BHA & Bits
        InputSpec("bha_table", "BHA Plan",
                  "table", columns=["Section", "BHA Type", "Bit (in)",
                                    "Motor/RSS", "MWD/LWD", "DC/HWDP (m)"],
                  group="8. BHA"),
        InputSpec("bit_table", "Bit Program",
                  "table", columns=["Section", "Type", "Size (in)", "IADC",
                                    "Manufacturer/Model"],
                  group="8. BHA"),
        # -- Parameters & Hydraulics
        InputSpec("drilling_params_table", "Drilling Parameters",
                  "table", columns=["Section", "WOB (klbs)", "RPM",
                                    "Flow (GPM)", "Max SPP (psi)",
                                    "Max Torque (ft-lbs)", "Overpull (klbs)"],
                  group="9. Parameters"),
        InputSpec("ann_velocity", "Min Annular Velocity", "number",
                  unit="ft/min", default="120", group="9. Parameters"),
        InputSpec("nozzle_velocity", "Nozzle Velocity", "number",
                  unit="ft/s", group="9. Parameters"),
        InputSpec("hsi", "HSI", "number", unit="HP/sq.in",
                  group="9. Parameters"),
        InputSpec("ecd_max", "Max ECD", "number", unit="ppg",
                  group="9. Parameters"),
        InputSpec("rop_target", "ROP Target", "number", unit="m/hr",
                  group="9. Parameters"),
        # -- Well control
        InputSpec("bop_stack", "BOP Stack", "text",
                  placeholder="e.g. Annular + Double Ram + Single Ram",
                  group="10. Well Control"),
        InputSpec("bop_wp", "BOP WP", "combo", options=["5000", "10000",
                  "15000"], unit="psi", group="10. Well Control"),
        InputSpec("bop_low_test", "BOP Low Test", "number", unit="psi",
                  default="250", group="10. Well Control"),
        InputSpec("bop_high_test", "BOP High Test (70% WP)", "number",
                  unit="psi", group="10. Well Control"),
        InputSpec("maasp", "MAASP at Shoe", "number", unit="psi",
                  group="10. Well Control"),
        InputSpec("kick_tolerance", "Kick Tolerance", "number", unit="bbl",
                  group="10. Well Control"),
        InputSpec("slow_pump_rates", "Slow Pump Rates", "text",
                  placeholder="e.g. 30 spm / 850 psi; 20 spm / 620 psi",
                  group="10. Well Control"),
        InputSpec("kill_method", "Primary Kill Method", "combo",
                  options=["Driller's Method", "Wait & Weight",
                           "Bullheading", "Volumetric"],
                  group="10. Well Control"),
        # -- Evaluation
        InputSpec("evaluation_table", "Evaluation Program",
                  "table", columns=["Interval", "Tool/Service", "Provider",
                                    "Duration (hrs)", "Purpose"],
                  group="11. Evaluation"),
        InputSpec("coring", "Coring", "text",
                  placeholder="e.g. 30m core in main reservoir — 4\" core",
                  group="11. Evaluation"),
        InputSpec("dst", "DST", "text", placeholder="e.g. 1 DST in S4",
                  group="11. Evaluation"),
        InputSpec("sampling", "Sampling", "text",
                  placeholder="e.g. PVT + oil/gas/water samples",
                  group="11. Evaluation"),
        # -- Completion
        InputSpec("completion_type", "Completion Type", "text",
                  placeholder="e.g. ESP completion", group="12. Completion"),
        InputSpec("completion_summary", "Completion Summary", "textarea",
                  placeholder="e.g. 4-1/2\" tubing, TRSV, SSD, packer, ESP",
                  group="12. Completion"),
        InputSpec("packer_depth", "Packer Depth", "number", unit="m",
                  group="12. Completion"),
        InputSpec("trsv_depth", "TRSV Depth", "number", unit="m",
                  group="12. Completion"),
        InputSpec("ssd_depth", "SSD Depth", "number", unit="m",
                  group="12. Completion"),
        InputSpec("tubing_string", "Tubing", "text",
                  placeholder="e.g. 4-1/2\" 18.9# L-80 VAM TOP",
                  group="12. Completion"),
        # -- Time & Cost
        InputSpec("time_table", "Time Breakdown",
                  "table", columns=["Phase", "Duration (days)",
                                    "Cumulative (days)"],
                  group="13. Time & Cost"),
        InputSpec("total_days", "Total Estimated Days", "number",
                  unit="days", group="13. Time & Cost"),
        InputSpec("npt_percent", "NPT Contingency", "number", unit="%",
                  default="10", group="13. Time & Cost"),
        InputSpec("cost_table", "Cost Estimate",
                  "table", columns=["Item", "Cost (USD)", "Remarks"],
                  group="13. Time & Cost"),
        InputSpec("total_cost", "Total Estimated Cost", "number",
                  unit="USD", group="13. Time & Cost"),
        InputSpec("cost_per_m", "Cost per Meter", "number", unit="USD/m",
                  group="13. Time & Cost"),
        # -- HSE
        InputSpec("h2s_drills", "H2S Drill Frequency", "combo",
                  options=["Weekly", "Monthly", "Per tour"],
                  group="14. HSE"),
        InputSpec("waste_plan", "Waste Management Plan", "text",
                  placeholder="e.g. zero discharge / pit burial",
                  group="14. HSE"),
        InputSpec("backup_equipment", "Backup Equipment List", "text",
                  placeholder="e.g. spare torque gauge, tongs, pumps",
                  group="14. HSE"),
        InputSpec("winterization", "Winterization", "combo",
                  options=["Not required", "Required", "Partial"],
                  group="14. HSE"),
    ],
    markdown=ADVANCED_DRILLING_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 12. HPHT DRILLING PROGRAM (NORTH SEA / SHELL-STYLE)
# ----------------------------------------------------------------------------

HPHT_PROGRAM_MD = r"""
# HPHT DRILLING PROGRAM — {{well_name}}

**Field:** {{field_name}} | **Operator:** {{operator}} | **Rig:** {{rig_name}}
**Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. SCOPE

Drill and complete HPHT well **{{well_name}}** (reservoir temperature
{{reservoir_temperature}} °F, pressure {{reservoir_pressure}} psi —
pressure gradient {{pressure_gradient}} psi/ft) in accordance with
HPHT standards (NORSOK D-010, API, Shell DEP / operator policy).

## 2. HPHT DESIGN PHILOSOPHY

1. **Well control is primary:** BOP rated {{bop_wp}} psi, tested to
   {{bop_test}} psi; secondary barrier always available.
2. **Design factors raised:** burst {{df_burst}}, collapse
   {{df_collapse}}, tension {{df_tension}}.
3. **Temperature de-rating** applied to all elastomers and casing
   ratings at {{reservoir_temperature}} °F.
4. **Gas-tight connections** required on all production casing/tubing.
5. **H2S / CO2:** {{h2s}} / {{co2}} — NACE MR-0175 materials.

## 3. WELL DATA

| Parameter | Value |
|---|---|
| Well | {{well_name}} |
| Field | {{field_name}} |
| TD MD / TVD | {{td_md}} / {{td_tvd}} m |
| Reservoir Temperature | {{reservoir_temperature}} °F |
| Reservoir Pressure | {{reservoir_pressure}} psi |
| Pore Pressure Gradient | {{pressure_gradient}} psi/ft |
| Fracture Gradient | {{frac_gradient}} ppg |
| Mud Weight Range | {{mud_range}} ppg |
| H2S | {{h2s}} |
| CO2 | {{co2}} |

## 4. CASING & MUD PROGRAM

{{casing_table}}

{{mud_table}}

## 5. WELL CONTROL

- MAASP at deepest shoe: {{maasp}} psi.
- Kick tolerance: {{kick_tolerance}} bbl.
- Kick detection: pit gain {{pit_gain}} bbl; flow {{flow_alarm}}.
- Shut-in procedure: {{shut_in_procedure}}.
- HPHT-specific: kick while tripping — stripping procedure
  {{stripping}}; gas handling via {{gas_handling}}.
- BOP: {{bop_stack}} ({{bop_wp}} psi); annular tested every
  {{annular_test_freq}}.

## 6. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Pre-spud | HPHT well control plan approved; BOP tested |
| HP-02 | Each casing | LOT/FIT; casing & cement accepted |
| HP-03 | TD | TD confirmed; logs accepted |
| HP-04 | Completion | Wellhead & completion tested |

## 7. CONTINGENCIES (HPHT)

- **Kick at high temp:** circulate with chillers; monitor BOP elastomers.
- **Lost circulation in HPHT:** small margin — reduce MW only with
  pore-pressure verification; balanced plug.
- **Tool failure at high temp:** HT-rated tools only; backups on
  location ({{ht_backups}}).
- **Gas at surface:** divert via HPHT choke manifold; H2S plan.

## 8. HSE (HPHT)

- Gas detection, wind socks, BA/SCBA, H2S watch ({{h2s}}).
- Emergency response and evacuation plan for remote location.
- Temperature management: hydrate/chill lines as required.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Reviewed By | {{reviewed_by}} | | |
| Approved By | {{approved_by}} | | |
"""

HPHT_PROGRAM = TemplateDef(
    key="hpht_drilling_program",
    name="HPHT Drilling Program (North Sea style)",
    icon="🌡️",
    kind="Program",
    description=(
        "High-pressure high-temperature drilling program — Shell/NORSOK "
        "style: HPHT design philosophy, derating, well control with "
        "stripping, gas handling, raised design factors."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  group="Well"),
        InputSpec("field_name", "Field", "text", group="Well"),
        InputSpec("operator", "Operator", "text", group="Well"),
        InputSpec("rig_name", "Rig", "text", group="Well"),
        InputSpec("td_md", "TD MD", "number", unit="m", group="Well"),
        InputSpec("td_tvd", "TD TVD", "number", unit="m", group="Well"),
        InputSpec("reservoir_temperature", "Reservoir Temperature", "number",
                  unit="°F", group="Reservoir"),
        InputSpec("reservoir_pressure", "Reservoir Pressure", "number",
                  unit="psi", group="Reservoir"),
        InputSpec("pressure_gradient", "Pore Pressure Gradient", "number",
                  unit="psi/ft", group="Reservoir"),
        InputSpec("frac_gradient", "Fracture Gradient", "number", unit="ppg",
                  group="Reservoir"),
        InputSpec("h2s", "H2S", "text", placeholder="e.g. 100 ppm",
                  group="Reservoir"),
        InputSpec("co2", "CO2", "text", placeholder="e.g. 5%",
                  group="Reservoir"),
        InputSpec("mud_range", "Mud Weight Range", "text",
                  placeholder="e.g. 14.5 - 17.5 ppg", group="Design"),
        InputSpec("df_burst", "DF Burst", "number", default="1.15",
                  group="Design"),
        InputSpec("df_collapse", "DF Collapse", "number", default="1.10",
                  group="Design"),
        InputSpec("df_tension", "DF Tension", "number", default="1.60",
                  group="Design"),
        InputSpec("casing_table", "Casing Program",
                  "table", columns=["Section", "Hole (in)", "Depth (m)",
                                    "Casing (in)", "Grade", "Conn"],
                  required=True, group="Design"),
        InputSpec("mud_table", "Mud Program",
                  "table", columns=["Section", "Type", "MW (ppg)",
                                    "HT/HP FL (ml)", "Remarks"],
                  group="Design"),
        InputSpec("bop_stack", "BOP Stack", "text",
                  placeholder="e.g. 15K annular + 2 x pipe + blind/shear",
                  group="Well Control"),
        InputSpec("bop_wp", "BOP WP", "combo", options=["10000", "15000",
                  "20000"], unit="psi", group="Well Control"),
        InputSpec("bop_test", "BOP Test Pressure", "number", unit="psi",
                  group="Well Control"),
        InputSpec("maasp", "MAASP", "number", unit="psi", group="Well Control"),
        InputSpec("kick_tolerance", "Kick Tolerance", "number", unit="bbl",
                  group="Well Control"),
        InputSpec("pit_gain", "Pit Gain Alarm", "number", unit="bbl",
                  default="3", group="Well Control"),
        InputSpec("flow_alarm", "Flow Alarm", "text", group="Well Control"),
        InputSpec("shut_in_procedure", "Shut-in Procedure", "textarea",
                  group="Well Control"),
        InputSpec("stripping", "Stripping Procedure", "textarea",
                  group="Well Control"),
        InputSpec("gas_handling", "Gas Handling", "text",
                  placeholder="e.g. HPHT choke manifold to separator",
                  group="Well Control"),
        InputSpec("annular_test_freq", "Annular Test Frequency", "combo",
                  options=["Daily", "Weekly"], group="Well Control"),
        InputSpec("ht_backups", "HT-Rated Backups", "text",
                  placeholder="e.g. spare HT MWD, HT packer",
                  group="Contingency"),
    ],
    markdown=HPHT_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 13. DEEPWATER DRILLING PROGRAM (GOM STYLE)
# ----------------------------------------------------------------------------

DEEPWATER_PROGRAM_MD = r"""
# DEEPWATER DRILLING PROGRAM — {{well_name}}

**Field:** {{field_name}} | **Operator:** {{operator}} | **Rig:** {{rig_name}}
**Water Depth:** {{water_depth}} m | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. SCOPE

Drill and complete deepwater well **{{well_name}}** in {{water_depth}} m
water depth with a {{rig_type}} in accordance with deepwater industry
practice (API RP 96, NORSOK D-010, operator DW procedures).

## 2. DEEPWATER DESIGN PHILOSOPHY

1. **Shallow hazards first:** shallow gas / water flow evaluation before
   spud ({{shallow_hazards}}).
2. **Subsea BOP** ({{bop_wp}} psi) with ROV intervention capability.
3. **Narrow mud window:** managed pressure / dual gradient as required
   ({{mpd_required}}).
4. **Riser management:** disconnect criteria defined ({{disconnect_criteria}}).
5. **Hydrates:** inhibition strategy {{hydrate_plan}}.

## 3. WELL DATA

| Parameter | Value |
|---|---|
| Well | {{well_name}} |
| Water Depth | {{water_depth}} m |
| RKB-MSL (air gap) | {{air_gap}} m |
| TD MD / TVD | {{td_md}} / {{td_tvd}} m |
| Target | {{target_formation}} |
| Reservoir Pressure | {{reservoir_pressure}} psi |
| Mud Weight Range | {{mud_range}} ppg |
| H2S / CO2 | {{h2s}} / {{co2}} |

## 4. CASING & MUD PROGRAM

{{casing_table}}

{{mud_table}}

## 5. WELL CONTROL (DEEPWATER)

- BOP: {{bop_stack}} — {{bop_wp}} psi, tested per API RP 53.
- Kick tolerance / MAASP: {{maasp}} psi at shoe.
- Disconnect sequence tested: {{disconnect_test}}.
- MPD / DGD: {{mpd_required}} ({{mpd_details}}).
- Shallow gas contingency: {{shallow_gas_plan}}.

## 6. RISER & MOORING

- Riser: {{riser}} with {{riser_tensioners}} tensioners.
- Vortex-induced vibration suppression: {{viv}}.
- Mooring: {{mooring}} — offset limits {{offset_limits}}.
- DP capability (if drillship): {{dp_capability}}.

## 7. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Pre-spud | Shallow hazard assessment approved |
| HP-02 | Jetting conductor | Conductor depth confirmed |
| HP-03 | Each casing | LOT/FIT; casing & cement accepted |
| HP-04 | TD | TD confirmed; logs accepted |

## 8. CONTINGENCIES

- **Shallow water flow:** activate SWF plan ({{swf_plan}}).
- **Lost returns:** MPD assist, LCM, plug; monitor annulus.
- **Hydrate plug:** inhibit, avoid long shut-ins, hydrate remediation
  ({{hydrate_remediation}}).
- **Riser disconnect:** per disconnect matrix ({{disconnect_matrix}}).

## 9. HSE (DEEPWATER)

- Simultaneous operations plan ({{simo}}).
- Emergency disconnect system tested before spud.
- Dropped object prevention; ROV operations plan.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Reviewed By | {{reviewed_by}} | | |
| Approved By | {{approved_by}} | | |
"""

DEEPWATER_PROGRAM = TemplateDef(
    key="deepwater_drilling_program",
    name="Deepwater Drilling Program (GOM style)",
    icon="🌊",
    kind="Program",
    description=(
        "Deepwater drilling program — API RP 96 style: shallow hazards, "
        "subsea BOP, riser & mooring, hydrates, MPD, disconnect matrix."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  group="Well"),
        InputSpec("field_name", "Field", "text", group="Well"),
        InputSpec("operator", "Operator", "text", group="Well"),
        InputSpec("rig_name", "Rig", "text", group="Well"),
        InputSpec("rig_type", "Rig Type", "combo",
                  options=["Drillship", "Semi-Submersible", "Jack-Up (shallow)"],
                  group="Well"),
        InputSpec("water_depth", "Water Depth", "number", unit="m",
                  required=True, group="Well"),
        InputSpec("air_gap", "Air Gap", "number", unit="m", group="Well"),
        InputSpec("td_md", "TD MD", "number", unit="m", group="Well"),
        InputSpec("td_tvd", "TD TVD", "number", unit="m", group="Well"),
        InputSpec("target_formation", "Target", "text", group="Well"),
        InputSpec("reservoir_pressure", "Reservoir Pressure", "number",
                  unit="psi", group="Reservoir"),
        InputSpec("mud_range", "Mud Weight Range", "text", group="Design"),
        InputSpec("h2s", "H2S", "text", group="Reservoir"),
        InputSpec("co2", "CO2", "text", group="Reservoir"),
        InputSpec("shallow_hazards", "Shallow Hazards Assessment", "textarea",
                  placeholder="e.g. 3D seismic review, SWF risk low",
                  group="Design"),
        InputSpec("bop_stack", "Subsea BOP Stack", "text",
                  placeholder="e.g. 18-3/4\" 15K, 4 ram + annular",
                  group="Well Control"),
        InputSpec("bop_wp", "BOP WP", "combo", options=["10000", "15000"],
                  unit="psi", group="Well Control"),
        InputSpec("maasp", "MAASP at Shoe", "number", unit="psi",
                  group="Well Control"),
        InputSpec("mpd_required", "MPD / Dual Gradient", "combo",
                  options=["Not required", "MPD", "DGD"],
                  group="Well Control"),
        InputSpec("mpd_details", "MPD Details", "textarea",
                  group="Well Control"),
        InputSpec("disconnect_criteria", "Disconnect Criteria", "textarea",
                  group="Well Control"),
        InputSpec("disconnect_test", "Disconnect Test", "text",
                  placeholder="e.g. weekly function test", group="Well Control"),
        InputSpec("shallow_gas_plan", "Shallow Gas Plan", "textarea",
                  group="Well Control"),
        InputSpec("casing_table", "Casing Program",
                  "table", columns=["Section", "Hole (in)", "Depth (m)",
                                    "Casing (in)", "Grade", "Conn"],
                  required=True, group="Design"),
        InputSpec("mud_table", "Mud Program",
                  "table", columns=["Section", "Type", "MW (ppg)", "Remarks"],
                  group="Design"),
        InputSpec("riser", "Riser", "text", group="Riser"),
        InputSpec("riser_tensioners", "Tensioners", "text", group="Riser"),
        InputSpec("viv", "VIV Suppression", "text", group="Riser"),
        InputSpec("mooring", "Mooring / DP", "text", group="Riser"),
        InputSpec("offset_limits", "Offset Limits", "text", group="Riser"),
        InputSpec("dp_capability", "DP Capability", "text", group="Riser"),
        InputSpec("swf_plan", "Shallow Water Flow Plan", "textarea",
                  group="Contingency"),
        InputSpec("hydrate_plan", "Hydrate Inhibition", "textarea",
                  group="Contingency"),
        InputSpec("hydrate_remediation", "Hydrate Remediation", "textarea",
                  group="Contingency"),
        InputSpec("disconnect_matrix", "Disconnect Matrix", "textarea",
                  group="Contingency"),
        InputSpec("simo", "Simultaneous Operations", "text",
                  group="HSE"),
    ],
    markdown=DEEPWATER_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# 14. HORIZONTAL / ERD SHALE PROGRAM
# ----------------------------------------------------------------------------

SHALE_PROGRAM_MD = r"""
# HORIZONTAL SHALE / ERD DRILLING PROGRAM — {{well_name}}

**Field / Play:** {{field_name}} | **Operator:** {{operator}} | **Rig:** {{rig_name}}
**Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. SCOPE

Drill and complete horizontal well **{{well_name}}** in the
**{{target_formation}}** shale play: vertical section to
{{vertical_td}} m, curve, and {{lateral_length}} m lateral.

## 2. DESIGN SUMMARY

| Parameter | Value |
|---|---|
| Well | {{well_name}} |
| Lateral Length | {{lateral_length}} m |
| KOP / Build | {{kop}} m / {{build_rate}} °/30m |
| Landing Depth | {{landing_depth}} m MD |
| Target Formation | {{target_formation}} |
| Mud System | {{mud_type}} |
| Casing / Liner | {{casing_program}} |
| Completion | {{completion_type}} ({{frac_stages}} stages) |

## 3. DRILLING PLAN

### 3.1 Vertical / Curve Sections

1. Drill vertical to KOP ({{kop}} m) with {{vertical_mud}}.
2. Build at {{build_rate}} °/30m to {{hold_inclination}}°.
3. Land at {{landing_depth}} m MD / {{landing_tvd}} m TVD.

### 3.2 Lateral

1. Drill lateral with RSS ({{rss_type}}) + rotary steerable BHA.
2. Maintain inclination {{hold_inclination}}° ± {{inc_tolerance}}°.
3. Geosteer with LWD ({{lwd_sensors}}).
4. TD at {{lateral_td}} m MD.

## 4. DRILLING PARAMETERS (LATERAL)

| Parameter | Value |
|---|---|
| WOB | {{wob}} klbs |
| RPM | {{rpm}} |
| Flow | {{flow}} gpm |
| Max SPP | {{spp}} psi |
| Torque (max) | {{torque}} ft-lbs |
| ROP (planned) | {{rop}} m/hr |
| Slide / rotate ratio | {{slide_ratio}} |

## 5. WELL CONTROL

- BOP: {{bop_stack}} ({{bop_wp}} psi).
- MAASP: {{maasp}} psi.
- Kick tolerance: {{kick_tolerance}} bbl.
- Pit gain alarm: {{pit_gain}} bbl.

## 6. COMPLETION (MULTI-STAGE)

- Open-hole or cased-hole: {{completion_type}}.
- Stages: {{frac_stages}} — cluster spacing {{cluster_spacing}} m.
- Isolation: {{isolation}}.
- Stimulation fluid: {{frac_fluid}}.

## 7. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | KOP | Vertical section complete; casing set |
| HP-02 | Landing | Curve landed per plan |
| HP-03 | Lateral | Lateral TD confirmed |
| HP-04 | Completion | Completion / frac plan approved |

## 8. CONTINGENCIES

- **Lateral instability:** keep ECD low, use {{stability_additive}},
  sweep pills.
- **Stuck in lateral:** work/jar, torque limits
  ({{torque_limits}}).
- **Geosteering off plan:** update model with LWD, adjust trajectory.

## 9. HSE

- High pump pressures during frac — barricade, tested iron.
- Chemical handling per SDS ({{frac_fluid}}).

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Reviewed By | {{reviewed_by}} | | |
| Approved By | {{approved_by}} | | |
"""

SHALE_PROGRAM = TemplateDef(
    key="horizontal_shale_program",
    name="Horizontal Shale / ERD Program",
    icon="↔️",
    kind="Program",
    description=(
        "Horizontal shale / ERD well program: vertical, curve, lateral "
        "drilling with RSS and geosteering, multi-stage completion."),
    inputs=[
        InputSpec("well_name", "Well Name", "text", required=True,
                  group="Well"),
        InputSpec("field_name", "Field / Play", "text", group="Well"),
        InputSpec("operator", "Operator", "text", group="Well"),
        InputSpec("rig_name", "Rig", "text", group="Well"),
        InputSpec("target_formation", "Target Formation", "text",
                  group="Well"),
        InputSpec("vertical_td", "Vertical Section TD", "number", unit="m",
                  group="Well"),
        InputSpec("lateral_length", "Lateral Length", "number", unit="m",
                  group="Well"),
        InputSpec("kop", "KOP", "number", unit="m", group="Well"),
        InputSpec("build_rate", "Build Rate", "number", unit="°/30m",
                  group="Well"),
        InputSpec("hold_inclination", "Hold Inclination", "number", unit="°",
                  group="Well"),
        InputSpec("inc_tolerance", "Inclination Tolerance", "number",
                  unit="°", default="1", group="Well"),
        InputSpec("landing_depth", "Landing Depth", "number", unit="m MD",
                  group="Well"),
        InputSpec("landing_tvd", "Landing TVD", "number", unit="m",
                  group="Well"),
        InputSpec("lateral_td", "Lateral TD", "number", unit="m MD",
                  group="Well"),
        InputSpec("mud_type", "Mud System", "combo",
                  options=["WBM - KCl/Polymer", "OBM - Mineral Oil", "SBM",
                           "High-performance WBM"],
                  group="Drilling"),
        InputSpec("vertical_mud", "Vertical Section Mud", "text",
                  group="Drilling"),
        InputSpec("rss_type", "RSS Type", "text",
                  placeholder="e.g. push-the-bit RSS", group="Drilling"),
        InputSpec("lwd_sensors", "LWD Sensors", "text",
                  placeholder="e.g. GR, RES, DNI (geosteering)",
                  group="Drilling"),
        InputSpec("wob", "WOB", "number", unit="klbs", group="Drilling"),
        InputSpec("rpm", "RPM", "number", group="Drilling"),
        InputSpec("flow", "Flow", "number", unit="gpm", group="Drilling"),
        InputSpec("spp", "Max SPP", "number", unit="psi", group="Drilling"),
        InputSpec("torque", "Max Torque", "number", unit="ft-lbs",
                  group="Drilling"),
        InputSpec("rop", "Planned ROP", "number", unit="m/hr",
                  group="Drilling"),
        InputSpec("slide_ratio", "Slide / Rotate Ratio", "text",
                  group="Drilling"),
        InputSpec("casing_program", "Casing / Liner Program", "text",
                  placeholder="e.g. 9-5/8\" surface + 5-1/2\" production casing",
                  group="Drilling"),
        InputSpec("bop_stack", "BOP Stack", "text", group="Well Control"),
        InputSpec("bop_wp", "BOP WP", "combo", options=["5000", "10000",
                  "15000"], unit="psi", group="Well Control"),
        InputSpec("maasp", "MAASP", "number", unit="psi", group="Well Control"),
        InputSpec("kick_tolerance", "Kick Tolerance", "number", unit="bbl",
                  group="Well Control"),
        InputSpec("pit_gain", "Pit Gain Alarm", "number", unit="bbl",
                  default="5", group="Well Control"),
        InputSpec("completion_type", "Completion", "combo",
                  options=["Cased-hole plug & perf", "Open-hole multi-stage",
                           "Cemented sleeve"],
                  group="Completion"),
        InputSpec("frac_stages", "Frac Stages", "number", group="Completion"),
        InputSpec("cluster_spacing", "Cluster Spacing", "number", unit="m",
                  group="Completion"),
        InputSpec("isolation", "Isolation Method", "text",
                  placeholder="e.g. dissolvable plugs", group="Completion"),
        InputSpec("frac_fluid", "Frac Fluid", "text",
                  placeholder="e.g. slickwater + sand", group="Completion"),
        InputSpec("stability_additive", "Stability Additive", "text",
                  placeholder="e.g. KCl, amine shale inhibitor",
                  group="Contingency"),
        InputSpec("torque_limits", "Torque Limits", "text",
                  placeholder="e.g. max 25,000 ft-lbs", group="Contingency"),
    ],
    markdown=SHALE_PROGRAM_MD,
)

# ----------------------------------------------------------------------------
# REGISTRY
# ----------------------------------------------------------------------------

ALL_TEMPLATES: List[TemplateDef] = [
    DRILLING_PROGRAM,
    ADVANCED_DRILLING_PROGRAM,
    WORKOVER_PROGRAM,
    ESP_WORKOVER,
    ABANDONMENT_PROGRAM,
    WELL_KILL_PROGRAM,
    CEMENTING_PROGRAM,
    WELL_TESTING_PROGRAM,
    FISHING_PROGRAM,
    STIMULATION_PROGRAM,
    COILED_TUBING_PROGRAM,
    HPHT_PROGRAM,
    DEEPWATER_PROGRAM,
    SHALE_PROGRAM,
]
