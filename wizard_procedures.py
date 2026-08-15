# ============================================================================
# PROCEDURE TEMPLATE LIBRARY
# ============================================================================
# Step-by-step operational procedures based on worldwide industry practice
# (API RP 53/59, IADC, NORSOK D-010, vendor OEM procedures). Each procedure
# contains: objective, pre-job checklist, step-by-step, tests and HSE.
# ============================================================================

from typing import List
from wizard_engine import TemplateDef, InputSpec

# ----------------------------------------------------------------------------
# Helper: common well inputs
# ----------------------------------------------------------------------------

def _well_inputs(prefix: str = "") -> List[InputSpec]:
    return [
        InputSpec(f"{prefix}well_name", "Well Name", "text", required=True,
                  group="Well"),
        InputSpec(f"{prefix}field", "Field", "text", group="Well"),
        InputSpec(f"{prefix}rig", "Rig / Unit", "text", group="Well"),
        InputSpec(f"{prefix}h2s", "H2S Present", "combo", options=["NO", "YES"],
                  group="Well"),
    ]


# 1. TRIPPING (POOH/RIH) PROCEDURE
TRIPPING_PROC = TemplateDef(
    key="tripping_procedure",
    name="Tripping Procedure (POOH / RIH)",
    icon="🔄",
    kind="Procedure",
    description="Safe tripping procedure: prep, POOH/RIH speeds, fill-up "
                "requirements, trip tank monitoring and contingency.",
    inputs=_well_inputs() + [
        InputSpec("operation", "Operation", "combo", options=["POOH", "RIH",
                  "POOH then RIH (bit change)"], group="Trip"),
        InputSpec("depth", "Current / Target Depth", "number", unit="m",
                  group="Trip"),
        InputSpec("hole_size", "Hole Size", "number", unit="in",
                  group="Trip"),
        InputSpec("string", "String Description", "text",
                  placeholder="e.g. 5\" DP + 8\" DC x 200m",
                  group="Trip"),
        InputSpec("mud_weight", "Mud Weight", "number", unit="ppg",
                  group="Trip"),
        InputSpec("trip_speed", "Max Trip Speed (empty hole)", "number",
                  unit="m/min", default="15", group="Trip"),
        InputSpec("trip_speed_cased", "Max Trip Speed (cased hole)", "number",
                  unit="m/min", default="25", group="Trip"),
        InputSpec("fill_interval", "Fill-Up Interval", "number", unit="stands",
                  default="5", group="Trip"),
        InputSpec("pull_limits", "Pull / Slack-off Limits", "text",
                  placeholder="e.g. pull 50k over string weight",
                  group="Trip"),
        InputSpec("trip_tank", "Trip Tank Monitoring", "combo",
                  options=["YES - continuous", "NO"],
                  group="Trip"),
    ],
    markdown=r"""
# TRIPPING PROCEDURE ({{operation}}) — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Perform safe tripping ({{operation}}) on well **{{well_name}}**
(current depth {{depth}} m) with continuous well control monitoring and
zero incidents.

## 2. PRE-JOB CHECKLIST

- [ ] String tally verified and updated
- [ ] Trip tank calibrated and lined up; pit volume totalizers working
- [ ] Fill-up pump lined up and tested
- [ ] Mud properties at {{mud_weight}} ppg within specification
- [ ] Well stable — no flow, no losses, no pressure build-up
- [ ] Crew instructed on speeds and communication (driller – floorman)
- [ ] H2S / gas monitoring active ({{h2s}})
- [ ] Slips and elevators inspected and sized correctly

## 3. PROCEDURE

### 3.1 Before Tripping

1. Circulate and condition mud (minimum {{condition_time}} min) until
   shakers clean and mud properties stable.
2. Record string weight (pick-up, rotating, slack-off).
3. Check trip tank level and zero the tank.
4. Brief crew: trip speed, fill-up interval, hand signals, emergency stops.

### 3.2 Pull Out of Hole (POOH)

1. Pull at controlled speed (max {{trip_speed_cased}} m/min cased /
   {{trip_speed}} m/min open hole).
2. Fill hole every {{fill_interval}} stands — record volume each time;
   expected fill: {{expected_fill}} bbl/stand.
3. Monitor trip tank continuously ({{trip_tank}}):
   - **Gain > {{trip_gain_alarm}} bbl** → stop, set slips, check flow —
     shut in if flowing.
   - **Loss > {{trip_loss_alarm}} bbl** → stop, check returns, treat losses.
4. Do not exceed pull limit {{pull_limits}}.
5. Set slips firmly; break out and lay down stands per routine.

### 3.3 Run In Hole (RIH)

1. RIH at controlled speed (max {{trip_speed_cased}} / {{trip_speed}}
   m/min).
2. Fill string every {{fill_interval}} stands; displace volume
   {{expected_fill}} bbl/stand.
3. Monitor trip tank for losses; if losses — stop and treat.
4. Slow down through casing shoe and BHA section
   ({{slow_zones}}).
5. At TD: tag gently, pick up, circulate and condition hole before
   drilling ahead.

## 4. WELL CONTROL RULES

- Trip tank gains/losses beyond alarm levels = **STOP** — never continue
  tripping.
- If flow observed: set slips, close BOP per drill, strip out as required.
- Maintain constant communication driller ↔ supervisor ↔ mud logger.

## 5. CONTINGENCIES

- **String stuck:** work pipe within limits, jar, back-off; fishing plan.
- **Lost circulation:** LCM pills; reduce trip speed; keep hole full.
- **Swab/kick:** shut in immediately; circulate per kill method.

## 6. HSE

- No hands on pipe while moving; use correct handling tools.
- Trip tank area barricaded; no smoking.
- Emergency stop signals known by all crew.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

TRIPPING_PROC.inputs += [
    InputSpec("condition_time", "Conditioning Time", "number", unit="min",
              default="30", group="Trip"),
    InputSpec("expected_fill", "Expected Fill/Displacement", "number",
              unit="bbl/stand", group="Trip"),
    InputSpec("trip_gain_alarm", "Trip Gain Alarm", "number", unit="bbl",
              default="5", group="Trip"),
    InputSpec("trip_loss_alarm", "Trip Loss Alarm", "number", unit="bbl",
              default="5", group="Trip"),
    InputSpec("slow_zones", "Slow Zones", "text",
              placeholder="e.g. 9-5/8\" shoe at 2000m, 7\" lap at 3200m",
              group="Trip"),
]

# 2. RUNNING CASING PROCEDURE
RUN_CASING_PROC = TemplateDef(
    key="running_casing_procedure",
    name="Running Casing Procedure",
    icon="🔧",
    kind="Procedure",
    description="Step-by-step casing running procedure: preparation, "
                "make-up/torque, fill, speed, contingency and cementing "
                "interface.",
    inputs=_well_inputs() + [
        InputSpec("casing_size", "Casing Size", "text", required=True,
                  placeholder="e.g. 9-5/8\" 53.5 ppf L-80 VAM TOP",
                  group="Casing"),
        InputSpec("setting_depth", "Setting Depth", "number", unit="m",
                  group="Casing"),
        InputSpec("hole_size", "Hole Size", "number", unit="in",
                  group="Casing"),
        InputSpec("joints", "Number of Joints", "number", unit="jts",
                  group="Casing"),
        InputSpec("connection", "Connection", "combo",
                  options=["BTC", "LTC", "VAM TOP", "TPG2", "HSM3", "Tenaris",
                           "Other premium"], group="Casing"),
        InputSpec("torque", "Make-Up Torque", "text",
                  placeholder="e.g. 8700 ft-lbs (optimum)",
                  group="Casing"),
        InputSpec("float_equipment", "Float Equipment", "text",
                  placeholder="e.g. float shoe + float collar + auto-fill",
                  group="Casing"),
        InputSpec("centralizers", "Centralizers", "text",
                  placeholder="e.g. bow-spring every 2 joints",
                  group="Casing"),
        InputSpec("running_speed", "Max Running Speed", "number", unit="m/min",
                  default="15", group="Casing"),
        InputSpec("fill_interval", "Fill-Up Interval", "number", unit="jts",
                  default="5", group="Casing"),
    ],
    markdown=r"""
# RUNNING CASING PROCEDURE — {{casing_size}} — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Run and land **{{casing_size}}** casing to {{setting_depth}} m
({{joints}} joints) in well **{{well_name}}**, ready for cementing,
without damage to the string or the well.

## 2. PRE-JOB CHECKLIST

- [ ] Casing tally prepared; joints drifted and measured
- [ ] Connections inspected and thread compound approved
- [ ] Tongs, backup, elevators, slips sized and tested
- [ ] Torque gauge calibrated (range covers {{torque}})
- [ ] Float equipment function tested (float shoe + collar)
- [ ] Centralizers counted and placed per plan ({{centralizers}})
- [ ] Fill-up lines and cement unit lined up
- [ ] Casing racking capacity confirmed
- [ ] Safety meeting held with casing crew

## 3. PROCEDURE

### 3.1 Preparation

1. Lay casing on catwalk/rack; inspect and clean threads.
2. Make up shoe track: float shoe + {{shoe_track}} joints + float collar.
3. Test float equipment: fill casing, confirm no backflow.
4. Pick up casing with elevators; stab into hole.

### 3.2 Make-Up

1. Stab and make up each connection with correct dope
   ({{connection}}).
2. Torque to: min {{torque_min}} / optimum {{torque}} / max
   {{torque_max}} ft-lbs.
3. Record torque-turn data on every joint ({{torque_log}}).
4. Stand back on slips; install centralizer per plan.

### 3.3 Running

1. RIH at max {{running_speed}} m/min; slow through tight zones and shoe
   ({{slow_zones}}).
2. Fill casing every {{fill_interval}} joints
   ({{fill_volume}} bbl/jt).
3. Monitor string weight and fill volumes — investigate any discrepancy.
4. On bottom: circulate ({{circulation_rate}} bpm) and condition hole
   ({{condition_time}} min) until clean.
5. Land casing in wellhead; install wear bushing if required.

## 4. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Prep | Tally, tools and torque gauge accepted |
| HP-02 | Shoe track | Float equipment tested |
| HP-03 | On bottom | Casing circulated; ready to cement |

## 5. CONTINGENCIES

- **Casing stuck:** work pipe, rotate within limits; circulate; if not
  free — POOH or cement as is with approval.
- **Connection leak during pressure test:** back off, re-dope, re-make,
  re-test.
- **Lost circulation while running:** fill continuously, LCM, reduce speed.

## 6. HSE

- Casing operations = high-risk lifting — barricade, correct handling tools.
- No personnel under suspended load; tongs guarded.
- Hand signals and radio communication agreed before starting.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

RUN_CASING_PROC.inputs += [
    InputSpec("shoe_track", "Shoe Track Joints", "number", default="2",
              group="Casing"),
    InputSpec("torque_min", "Torque Min", "text", placeholder="ft-lbs",
              group="Casing"),
    InputSpec("torque_max", "Torque Max", "text", placeholder="ft-lbs",
              group="Casing"),
    InputSpec("torque_log", "Torque-Turn Log", "combo", options=["YES", "NO"],
              group="Casing"),
    InputSpec("slow_zones", "Slow Zones", "text",
              placeholder="e.g. BHA section, shoe, 7\" lap",
              group="Casing"),
    InputSpec("fill_volume", "Fill Volume", "number", unit="bbl/jt",
              group="Casing"),
    InputSpec("circulation_rate", "Circulation Rate", "number", unit="bpm",
              default="8", group="Casing"),
    InputSpec("condition_time", "Conditioning Time", "number", unit="min",
              default="30", group="Casing"),
]

# 3. BOP PRESSURE TEST PROCEDURE
BOP_TEST_PROC = TemplateDef(
    key="bop_test_procedure",
    name="BOP Pressure Test Procedure",
    icon="🛑",
    kind="Procedure",
    description="BOP stack function and pressure test procedure per API RP 53: "
                "low/high pressure, sequence, hold times, documentation.",
    inputs=_well_inputs() + [
        InputSpec("bop_stack", "BOP Stack", "text", required=True,
                  placeholder="e.g. Annular + Double Ram + Single Ram 13-5/8\" 5K",
                  group="BOP"),
        InputSpec("wp", "Working Pressure", "number", unit="psi",
                  default="5000", group="BOP"),
        InputSpec("test_plug", "Test Tool / Plug", "text",
                  placeholder="e.g. 5\" test plug", group="BOP"),
        InputSpec("low_pressure", "Low Pressure Test", "number", unit="psi",
          default="250", group="BOP"),
        InputSpec("function_freq", "Function Test Frequency", "combo",
                  options=["Weekly", "Every 14 days", "Per section"],
                  group="BOP"),
    ],
    markdown=r"""
# BOP PRESSURE TEST PROCEDURE — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Pressure test and function test the BOP stack
(**{{bop_stack}}**, WP {{wp}} psi) on well **{{well_name}}** in accordance
with API RP 53 and company requirements.

## 2. PRE-JOB CHECKLIST

- [ ] Accumulator pre-charge and fluid volume verified
- [ ] Test pump and recorder calibrated
- [ ] Test plugs/rams sized to drill pipe in hole ({{test_plug}})
- [ ] All test charts/forms ready
- [ ] Kill/choke lines rigged and tested
- [ ] Crew assigned: driller, toolpusher, well control supervisor
- [ ] H2S watch active ({{h2s}})

## 3. PROCEDURE

### 3.1 Function Test

1. Function test each component **without pressure** (close/open):
   - Annular
   - Pipe rams ({{pipe_rams}})
   - Blind/shear rams
   - Choke & kill valves
2. Record closing times — must be within API limits
   ({{close_time}} seconds).
3. Function test frequency: {{function_freq}}.

### 3.2 Pressure Test Sequence

Test in the following order, always **low pressure first** then high:

| # | Component | Low (psi) | High (psi) | Hold (min) |
|---|---|---|---|---|
| 1 | Annular (on pipe) | {{low_pressure}} | {{annular_high}} | 10 |
| 2 | Pipe rams (on pipe) | {{low_pressure}} | {{ram_high}} | 15 |
| 3 | Blind/shear rams | {{low_pressure}} | {{ram_high}} | 15 |
| 4 | Choke manifold | {{low_pressure}} | {{choke_high}} | 10 |
| 5 | Kill manifold | {{low_pressure}} | {{kill_high}} | 10 |
| 6 | Accumulator (function) | — | {{acc_pressure}} | — |

1. Run test plug / string to depth and space out rams.
2. Close the component to be tested.
3. Pressure up slowly to low test ({{low_pressure}} psi); hold
   {{low_hold}} min; check for leaks.
4. Bleed to zero; pressure up to high test
   ({{high_test}} psi = 70% of WP); hold {{high_hold}} min.
5. **Acceptance:** no more than {{leak_tolerance}} psi drop over hold
   period.
6. Record pressures on the BOP test chart with signatures.

## 4. HOLD POINT

> **HP:** BOP test accepted by Company Supervisor + Client representative
> before drilling ahead / before operations continue.

## 5. CONTINGENCIES

- **Leak:** bleed off, identify, repair/replace seal, re-test.
- **Ram won't close:** function test again, check hydraulic circuit,
  repair before continuing.
- **Chart recorder failure:** repair/replace, re-run test — no test
  without record.

## 6. HSE

- High-pressure test zone barricaded; no personnel near BOP during test.
- Communication plan between BOP area and driller.
- Never exceed 70% of rated working pressure.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

BOP_TEST_PROC.inputs += [
    InputSpec("pipe_rams", "Pipe Rams", "text", placeholder="e.g. 5\" + 3-1/2\"",
              group="BOP"),
    InputSpec("close_time", "Max Closing Time", "number", unit="sec",
              default="30", group="BOP"),
    InputSpec("annular_high", "Annular High Test", "number", unit="psi",
              group="BOP"),
    InputSpec("ram_high", "Ram High Test", "number", unit="psi",
              group="BOP"),
    InputSpec("choke_high", "Choke Manifold High Test", "number", unit="psi",
              group="BOP"),
    InputSpec("kill_high", "Kill Manifold High Test", "number", unit="psi",
              group="BOP"),
    InputSpec("acc_pressure", "Accumulator Pressure", "number", unit="psi",
              default="3000", group="BOP"),
    InputSpec("high_test", "High Test Pressure (70% WP)", "number", unit="psi",
              group="BOP"),
    InputSpec("low_hold", "Low Hold Time", "number", unit="min", default="5",
              group="BOP"),
    InputSpec("high_hold", "High Hold Time", "number", unit="min", default="15",
              group="BOP"),
    InputSpec("leak_tolerance", "Leak Tolerance", "number", unit="psi",
              default="50", group="BOP"),
]

# 4. KICK CIRCULATION PROCEDURE (DRILLER'S METHOD)
KICK_PROC = TemplateDef(
    key="kick_circulation_procedure",
    name="Kick Circulation Procedure (Driller's Method)",
    icon="🔴",
    kind="Procedure",
    description="Shut-in and circulate a kick out with Driller's Method: "
                "detection, shut-in, ICP/FCP, circulation, verification.",
    inputs=_well_inputs() + [
        InputSpec("mud_weight", "Current Mud Weight", "number", unit="ppg",
                  group="Kill"),
        InputSpec("tvd", "TVD at TD", "number", unit="m", group="Kill"),
        InputSpec("sidpp", "SIDPP", "number", unit="psi", group="Kill"),
        InputSpec("sidpip", "SIDPIP", "number", unit="psi", group="Kill"),
        InputSpec("spp", "Slow Pump Pressure", "number", unit="psi",
                  group="Kill"),
        InputSpec("spm", "Slow Pump Rate", "number", unit="spm",
                  group="Kill"),
        InputSpec("pit_gain", "Pit Gain (kick size)", "number", unit="bbl",
                  group="Kill"),
    ],
    markdown=r"""
# KICK CIRCULATION PROCEDURE — DRILLER'S METHOD — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Safely shut in well **{{well_name}}** after a kick and circulate the
influx out using the **Driller's Method** (constant BHP), then weigh up
the mud to the kill weight.

## 2. DETECTION & SHUT-IN

### 2.1 Kick Indicators

- [ ] Pit gain > {{pit_gain}} bbl
- [ ] Flow from well with pumps off
- [ ] Flow increase with pumps on
- [ ] Drilling break
- [ ] Pump pressure change
- [ ] Trip tank gain/loss anomalies

### 2.2 Shut-In Sequence (drilling)

1. Pick up off bottom; set slips; stop rotary.
2. Stop pumps — check flow. If flow: **SHUT IN**.
3. Close BOP (annular first, then pipe rams).
4. Record: SIDPP = {{sidpp}} psi, SIDPIP = {{sidpip}} psi,
   pit gain = {{pit_gain}} bbl.
5. Notify supervisor; do not strip unless required.

## 3. CIRCULATION — DRILLER'S METHOD

### 3.1 First Circulation (remove kick)

1. Line up choke line; open choke.
2. Start pump at slow rate ({{spm}} spm); hold casing pressure at
   **SIDPP = {{sidpp}} psi** while bringing pump to speed.
3. When pump at speed: **ICP** = SPP ({{spp}} psi) + SIDPP
   ({{sidpp}} psi) = **{{icp}} psi** — hold ICP constant on the
   choke.
4. Circulate until kick is out (gas at surface) — monitor choke
   pressure; bleed gas at surface per procedure.
5. Stop pump; shut in. Verify: SIDPP ≈ SIDPIP (both equal after kick
   removed).

### 3.2 Second Circulation (weigh up)

1. **Kill Mud Weight** = MW + SIDPP / (0.052 × TVD)
   = {{mud_weight}} + {{sidpp}} / (0.052 × {{tvd}} m)
   = **{{kill_mw}} ppg**.
2. Weight up mud system to {{kill_mw}} ppg.
3. Start pump at {{spm}} spm; hold casing = final SIDPP; bring pump to
   speed.
4. **FCP** = SPP × (kill MW / old MW) = **{{fcp}} psi** — hold FCP on
   choke until kill mud reaches bit.
5. Continue circulating; when kill mud returns: shut in and verify
   SIDPP = 0, SIDPIP = 0.
6. Bleed pressure; open well; resume operations.

## 4. MONITORING

| Parameter | Target |
|---|---|
| Casing pressure (1st circ) | SIDPP = {{sidpp}} psi |
| ICP | {{icp}} psi |
| Kill mud weight | {{kill_mw}} ppg |
| FCP | {{fcp}} psi |
| Pit gain during circ | No increase |
| H2S | Monitor ({{h2s}}) |

## 5. HOLD POINT

> **HP:** Well dead (SIDPP = 0) — confirmed by Company Supervisor before
> resuming operations.

## 6. CONTINGENCIES

- **Cannot circulate:** bullhead per plan / CT.
- **Lost circulation while circulating:** reduce rate; LCM; keep choke
  control.
- **Gas at surface (H2S):** activate H2S plan, evacuate upwind,
  monitor.

## 7. HSE

- Choke manifold manned by trained crew; remote choke operation.
- Gas detection and H2S alarms active.
- No unnecessary personnel on rig floor during shut-in.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

KICK_PROC.inputs += [
    InputSpec("icp", "ICP (calculated)", "number", unit="psi",
              group="Kill"),
    InputSpec("kill_mw", "Kill Mud Weight (calculated)", "number", unit="ppg",
              group="Kill"),
    InputSpec("fcp", "FCP (calculated)", "number", unit="psi",
              group="Kill"),
]

# 5. STUCK PIPE / FREEING PROCEDURE
STUCK_PIPE_PROC = TemplateDef(
    key="stuck_pipe_procedure",
    name="Stuck Pipe / Jarring Procedure",
    icon="⛓️",
    kind="Procedure",
    description="Stuck pipe prevention and freeing: detection, work the "
                "string, jarring plan, spotting, back-off, fishing handover.",
    inputs=_well_inputs() + [
        InputSpec("depth", "Stuck Depth", "number", unit="m", group="Stuck"),
        InputSpec("string", "String", "text",
                  placeholder="e.g. 5\" DP + BHA", group="Stuck"),
        InputSpec("max_overpull", "Max Overpull", "number", unit="klbs",
                  group="Stuck"),
        InputSpec("free_point", "Free Point (if known)", "text",
                  placeholder="e.g. 2400m", group="Stuck"),
        InputSpec("jar", "Jars in String", "combo", options=["YES", "NO"],
                  group="Stuck"),
    ],
    markdown=r"""
# STUCK PIPE PROCEDURE — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Prevent and, if stuck, free the string in well **{{well_name}}** safely —
protecting hole, equipment and personnel.

## 2. PREVENTION (DAILY)

- [ ] Maintain mud properties per program ({{mud_props}})
- [ ] Monitor torque/drag trends; record every stand
- [ ] Ream/condition before connections and long trips
- [ ] Keep ECD within limits ({{ecd_max}} ppg)
- [ ] No excessive WOB/RPM; parameters per program
- [ ] Trip speeds per procedure; slow zones respected

## 3. DETECTION

- **While drilling:** overpull, torque increase, ROP drop, pump pressure
  change, pack-off.
- **While tripping:** overpull, string won't move, fill on bottom.

## 4. FREEING PROCEDURE

### 4.1 Initial Actions (first 30 minutes)

1. **STOP** — do not rotate/pull blindly.
2. Slack off to neutral; record weights (pick-up, slack-off, rotating).
3. If possible: **circulate** at max safe rate
   ({{circ_rate}} bpm) to clean and reduce differential sticking.
4. Work the pipe: pull to {{max_overpull}} klbs, slack off to
   {{slack_off}} klbs, × {{work_cycles}} cycles.
5. Rotate slowly ({{rotate_rpm}} rpm) if rotation is possible.

### 4.2 Jarring

1. Set jars per plan:
   - Up-jar: {{up_jar}} klbs over string weight, × {{up_cycles}}
     (hold {{jar_hold}} min between).
   - Down-jar: {{down_jar}} klbs slack-off, × {{down_cycles}}.
2. Record jarring count and progress every cycle.
3. If no progress after {{jar_timeout}} hrs: stop and evaluate.

### 4.3 Spotting & Back-Off

1. Spot pipe-release / oil pill: {{spot_pill}} ({{spot_volume}} bbl)
   across stuck interval ({{stuck_interval}}).
2. Soak time: {{soak_time}} hrs; re-work pipe periodically.
3. If still stuck: run free-point log ({{free_point}}), back-off at
   safety joint, POOH free string.
4. Decide with Company: fishing, sidetrack, or abandon fish
   ({{fish_decision}}).

## 5. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Detection | Stuck confirmed — inform office |
| HP-02 | Freeing | Jarring plan approved before starting |
| HP-03 | Decision | Back-off / fishing / sidetrack decision approved |

## 6. CONTINGENCIES

- **Differential sticking:** reduce MW (if safe), spot oil pill, keep
  circulation.
- **Mechanical sticking:** work/jar; clean annulus; washover if needed.
- **Kick during freeing:** shut in per well control procedure.

## 7. HSE

- Monitor pipe handling during heavy pulls — barricade drill floor.
- Communication: driller – supervisor – office on every cycle.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

STUCK_PIPE_PROC.inputs += [
    InputSpec("mud_props", "Mud Properties", "text",
              placeholder="e.g. 12.0 ppg, FL 4 ml", group="Prevention"),
    InputSpec("ecd_max", "Max ECD", "number", unit="ppg", group="Prevention"),
    InputSpec("circ_rate", "Circulation Rate", "number", unit="bpm",
              default="8", group="Freeing"),
    InputSpec("slack_off", "Slack-off Limit", "number", unit="klbs",
              group="Freeing"),
    InputSpec("work_cycles", "Work Cycles", "number", default="20",
              group="Freeing"),
    InputSpec("rotate_rpm", "Rotation RPM (if possible)", "number",
              default="40", group="Freeing"),
    InputSpec("up_jar", "Up-Jar Pull", "number", unit="klbs",
              group="Jarring"),
    InputSpec("up_cycles", "Up-Jar Cycles", "number", default="10",
              group="Jarring"),
    InputSpec("down_jar", "Down-Jar Slack", "number", unit="klbs",
              group="Jarring"),
    InputSpec("down_cycles", "Down-Jar Cycles", "number", default="10",
              group="Jarring"),
    InputSpec("jar_hold", "Hold Between Cycles", "number", unit="min",
              default="10", group="Jarring"),
    InputSpec("jar_timeout", "Jarring Timeout", "number", unit="hrs",
              default="4", group="Jarring"),
    InputSpec("spot_pill", "Spotting Pill", "text",
              placeholder="e.g. oil-based pipe release", group="Spotting"),
    InputSpec("spot_volume", "Pill Volume", "number", unit="bbl",
              group="Spotting"),
    InputSpec("stuck_interval", "Stuck Interval", "text",
              placeholder="e.g. 2380-2410m", group="Spotting"),
    InputSpec("soak_time", "Soak Time", "number", unit="hrs", default="12",
              group="Spotting"),
    InputSpec("fish_decision", "Fallback Decision", "combo",
              options=["Fishing", "Sidetrack", "Abandon fish in hole"],
              group="Decision"),
]

# 6. SLICKLINE PROCEDURE (PLUG / SSD)
SLICKLINE_PROC = TemplateDef(
    key="slickline_procedure",
    name="Slickline Procedure (Plug Setting / SSD Shift)",
    icon="📏",
    kind="Procedure",
    description="Slickline operation procedure: rig-up, pressure test, "
                "gauge run, plug setting / SSD shifting, POOH, verification.",
    inputs=_well_inputs() + [
        InputSpec("operation", "Operation", "combo",
                  options=["Set plug", "Pull plug", "Shift SSD",
                           "Gauge / drift run", "Set & retrieve protection sleeve",
                           "Retrieve plugs"],
                  group="SL"),
        InputSpec("tool_depth", "Tool Depth", "number", unit="m",
                  group="SL"),
        InputSpec("wire", "Wire / Rope", "combo",
                  options=["1-7/8\" slickline", "1-3/4\" slickline",
                           "3/16\" slickline"], group="SL"),
        InputSpec("lubricator", "Lubricator Length", "number", unit="ft",
                  default="60", group="SL"),
        InputSpec("bop_test", "SL BOP Test", "number", unit="psi",
                  default="2500", group="SL"),
        InputSpec("wellhead_pressure", "Wellhead Pressure", "number",
                  unit="psi", group="SL"),
    ],
    markdown=r"""
# SLICKLINE PROCEDURE ({{operation}}) — {{well_name}}

**Field:** {{field}} | **Rig/Unit:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Perform **{{operation}}** at {{tool_depth}} m in well **{{well_name}}**
with slickline ({{wire}}) safely and without damage to the completion.

## 2. PRE-JOB CHECKLIST

- [ ] Well static and under control (WHP {{wellhead_pressure}} psi)
- [ ] Lubricator ({{lubricator}} ft) sized to tool string
- [ ] SL BOP function tested; test pressure {{bop_test}} psi
- [ ] Wire inspected; rope socket and sinker bars checked
- [ ] Tools function tested at surface ({{tools}})
- [ ] Depth reference confirmed (wireline zero at {{zero_ref}})
- [ ] H2S monitoring active ({{h2s}})

## 3. PROCEDURE

### 3.1 Rig-Up

1. Rig up lubricator on tree; pressure test SL BOP and lubricator to
   {{bop_test}} psi (hold 10 min).
2. Run test bar / dummy run to confirm access
   ({{dummy_run}}).
3. Make up tool string: {{tool_string}}.

### 3.2 Run In Hole

1. RIH at max {{rih_speed}} m/min, monitoring weight.
2. Slow down through {{slow_zones}}.
3. Tag depth at {{tool_depth}} m; verify with {{tag_check}}.

### 3.3 Operation

{{operation_steps}}

### 3.4 POOH

1. POOH at controlled speed; check each stand.
2. Verify tool function at surface ({{surface_check}}).
3. Rig down; record final wellhead pressure.

## 4. TESTS & HOLD POINTS

| Test | Value | Hold |
|---|---|---|
| SL BOP / lubricator | {{bop_test}} psi | 10 min |
| Plug / SSD function | {{tool_test}} psi | 15 min |

> **HP:** Operation verified (depth, function, pressure) with Company
> Supervisor before rigging down.

## 5. CONTINGENCIES

- **Tool stuck:** work line within limits, jar; if not free — cut and
  fish per plan.
- **Line parted:** fish with wireline fishing tools; inform office.
- **Well starts flowing:** close SL BOP / tree valves, shut in.

## 6. HSE

- No personnel under lubricator; use proper line handling.
- Barricade wireline area; communication wireline operator ↔ driller.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

SLICKLINE_PROC.inputs += [
    InputSpec("tools", "Tools", "text",
              placeholder="e.g. plug 2.750\" + running tool", group="SL"),
    InputSpec("zero_ref", "Zero Reference", "text",
              placeholder="e.g. top of tree flange", group="SL"),
    InputSpec("dummy_run", "Dummy Run", "combo", options=["YES", "NO"],
              group="SL"),
    InputSpec("tool_string", "Tool String", "text",
              placeholder="e.g. rope socket + 2 sinkers + jar + tool",
              group="SL"),
    InputSpec("rih_speed", "Max RIH Speed", "number", unit="m/min",
              default="30", group="SL"),
    InputSpec("slow_zones", "Slow Zones", "text",
              placeholder="e.g. TRSV at 100m, SSD at 2300m",
              group="SL"),
    InputSpec("tag_check", "Tag Verification", "text",
              placeholder="e.g. weight change + depth correlation",
              group="SL"),
    InputSpec("operation_steps", "Operation Steps", "textarea",
              required=True, placeholder="1. Set plug in SSD profile...\n2. ...",
              group="SL"),
    InputSpec("surface_check", "Surface Check", "text",
              placeholder="e.g. plug firmly latched, prong retrieved",
              group="SL"),
    InputSpec("tool_test", "Tool Test Pressure", "number", unit="psi",
              default="2500", group="SL"),
]

# 7. ESP RUNNING PROCEDURE
ESP_RUN_PROC = TemplateDef(
    key="esp_running_procedure",
    name="ESP Running Procedure",
    icon="⚡",
    kind="Procedure",
    description="Step-by-step ESP assembly and running procedure: pre-run "
                "gate, assembly order, cable/CCCP, running rules, tests, "
                "packer, TRSV and splice interface.",
    inputs=_well_inputs() + [
        InputSpec("esp_supplier", "ESP Supplier", "text", group="ESP"),
        InputSpec("pump_model", "Pump / Motor Model", "text",
                  placeholder="e.g. REDA 400 series, 150 HP", group="ESP"),
        InputSpec("packer_depth", "Packer Depth", "number", unit="m",
                  group="ESP"),
        InputSpec("cable", "Cable Type", "text",
                  placeholder="e.g. #4 AWG redi-lead", group="ESP"),
        InputSpec("megger", "Megger Min IR", "number", unit="MΩ",
                  default="100", group="ESP"),
    ],
    markdown=r"""
# ESP RUNNING PROCEDURE — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Assemble and run the ESP completion (**{{pump_model}}**) in well
**{{well_name}}** to packer depth {{packer_depth}} m, with cable, MLE,
CCCPs and penetrators installed correctly, protecting the system and
the well. ESP supplier: {{esp_supplier}}.

## 2. PRE-RUN VERIFICATION GATE (MANDATORY)

Before any ESP equipment is moved to the rig floor, confirm ALL:

- [ ] ESP surface equipment installed and function tested
- [ ] All XOs physically assembled on bench
- [ ] Tubing drifted, measured, tallied; pup joints made up on tools
- [ ] CCCP + band-it straps available ({{cccp_qty}} pcs)
- [ ] Spooler, sheave, reel shaft verified
- [ ] Splice shelter + splice kits (primary + backup)
- [ ] Penetrators (primary + backup) verified
- [ ] Megger/multimeter calibrated
- [ ] Torque gauge and tongs (primary + backup) tested
- [ ] ESP vendor procedure and drawings available
- [ ] Well filled to surface; hole clean and drifted
- [ ] Pre-job safety meeting with ESP vendor + rig crew

## 3. ASSEMBLY (BOTTOM UP — ESP VENDOR SUPERVISION)

| # | Component | Responsibility |
|---|---|---|
| 1 | Centralizer | ESP Vendor |
| 2 | Sensor (DMS) | ESP Vendor |
| 3 | Motor(s) | ESP Vendor |
| 4 | Protector(s) | ESP Vendor |
| 5 | Intake | ESP Vendor |
| 6 | Gas separator | ESP Vendor |
| 7 | Pump sections | ESP Vendor |
| 8 | BOD + discharge sub | ESP Vendor |
| 9 | Shrouds / guards | ESP Vendor |

1. Assemble on the rig floor per vendor procedure; torque per OEM table.
2. Megger before and after each major connection
   (min {{megger}} MΩ).
3. Connect cable and MLE; dress cable with CCCP + 3 band-it straps per
   joint.
4. Lift and lower ESP into well slowly (no shock loading).

## 4. RUNNING SEQUENCE (ABOVE ESP)

1. Discharge pressure sub → 1 jt tubing → check valve assembly
2. 2 jts tubing → drain valve assembly → 1 jt tubing
3. SSD (closed, plug & prong) with XOs → continue tubing to
   {{lower_depth}} m
4. XO to 4-1/2\" → tubing to packer depth {{packer_depth}} m
5. Packer (with AGV, penetrators, CL) → 2 jts tubing
6. TRSV assembly with flow couplings + CL → ±6 jts tubing
7. Tubing hanger assembly → landing joint

> **Note:** No landing nipple in this ESP design (per master document).

## 5. RUNNING RULES

- Speed: {{running_speed}} m/min (first 50 m < 2 m/min).
- No shock loading; no unplanned rotation.
- Continuous driller–spooler communication; stop on any drag change.
- Fill string every 10 joints; fill annulus every hour.
- **Megger every 10 joints** (min {{megger}} MΩ, record values).
- Install CCCP + 3 band-it straps on each joint.

## 6. TESTS DURING RUN

| Test | Pressure | Hold |
|---|---|---|
| Check valve | {{check_valve_test}} psi | 15 min |
| Drain valve (against CV) | {{drain_valve_test}} psi | 15 min |
| SSD (against plug) | {{ssd_test}} psi | 10 min |
| String @ intermediate | {{string_test}} psi | 15 min |
| AGV control line | {{agv_test}} psi | 15 min |
| Packer connection (shallow) | {{packer_shallow_test}} psi | 15 min |

- Megger after every splice/penetrator installation.

## 7. PACKER & TRSV INSTALLATION

1. Make up packer with AGV + penetrators; connect AGV CL; test
   {{agv_test}} psi; open AGV, maintain {{agv_run_pressure}} psi.
2. Install cable penetrators; splice cable; test IR.
3. Make up TRSV with flow couplings; connect CL; test
   {{trsv_test}} psi; keep flapper open with {{trsv_hold_pressure}} psi.
4. Run gauge cutter through TRSV to verify ID.

## 8. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Gate | Pre-run verification accepted |
| HP-02 | ESP | ESP assembled and meggered OK |
| HP-03 | Tests | CV / drain valve / SSD tests accepted |
| HP-04 | Packer | Packer installed; AGV tested |
| HP-05 | TRSV | TRSV tested; splice ready |

## 9. CONTINGENCIES

- **IR drop:** stop, re-test; if sustained — consult vendor; do not
  continue below min IR.
- **Valve leak:** torque up, re-test, replace with backup.
- **Drag increase:** stop, work slowly, evaluate; do not force.

## 10. HSE

- ESP assembly = heavy lifts — certified lifting gear and riggers.
- No personnel under suspended ESP components.
- Electrical safety: lock-out/tag-out for all electrical connections.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

ESP_RUN_PROC.inputs += [
    InputSpec("cccp_qty", "CCCP Quantity", "text", placeholder="e.g. 240",
              group="ESP"),
    InputSpec("lower_depth", "Lower Completion Depth", "number", unit="m",
              group="ESP"),
    InputSpec("running_speed", "Running Speed", "number", unit="m/min",
              default="3", group="ESP"),
    InputSpec("check_valve_test", "Check Valve Test", "number", unit="psi",
              default="2500", group="Tests"),
    InputSpec("drain_valve_test", "Drain Valve Test", "number", unit="psi",
              default="2500", group="Tests"),
    InputSpec("ssd_test", "SSD Test", "number", unit="psi", default="2500",
              group="Tests"),
    InputSpec("string_test", "String Test", "number", unit="psi",
              default="3500", group="Tests"),
    InputSpec("agv_test", "AGV Line Test", "number", unit="psi",
              default="5000", group="Tests"),
    InputSpec("agv_run_pressure", "AGV Running Pressure", "number",
              unit="psi", default="2500", group="Tests"),
    InputSpec("packer_shallow_test", "Packer Shallow Test", "number",
              unit="psi", default="300", group="Tests"),
    InputSpec("trsv_test", "TRSV CL Test", "text", default="500/5000 psi",
              group="Tests"),
    InputSpec("trsv_hold_pressure", "TRSV Hold Pressure", "number",
              unit="psi", default="4000", group="Tests"),
]

# 8. PACKER SETTING PROCEDURE
PACKER_SET_PROC = TemplateDef(
    key="packer_setting_procedure",
    name="Packer Setting Procedure",
    icon="🪢",
    kind="Procedure",
    description="Hydraulic packer setting procedure: run-in, shear, set, "
                "test, overpull verification.",
    inputs=_well_inputs() + [
        InputSpec("packer", "Packer Type", "text", required=True,
                  placeholder="e.g. 9-5/8\" retrievable hydraulic w/ AGV",
                  group="Packer"),
        InputSpec("depth", "Setting Depth", "number", unit="m", group="Packer"),
        InputSpec("shear_pressure", "Shear Pressure", "number", unit="psi",
                  group="Packer"),
        InputSpec("set_pressure", "Setting Pressure", "number", unit="psi",
                  default="3500", group="Packer"),
        InputSpec("test_pressure", "Test Pressure (annulus)", "number",
                  unit="psi", default="1000", group="Packer"),
    ],
    markdown=r"""
# PACKER SETTING PROCEDURE — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Run and set **{{packer}}** at {{depth}} m in well **{{well_name}}**
and verify the seal with pressure tests.

## 2. PRE-JOB CHECKLIST

- [ ] Packer inspected; shear pins verified ({{shear_pressure}} psi)
- [ ] Setting tool function tested
- [ ] Tubing tally and space-out confirmed
- [ ] Pump truck lined up and tested (lines {{line_test}} psi)
- [ ] Packer depth correlated with gamma/CCL if required
- [ ] H2S watch ({{h2s}})

## 3. PROCEDURE

### 3.1 Run In Hole

1. RIH packer assembly at controlled speed
   (max {{rih_speed}} m/min).
2. Fill string per plan; monitor for any drag.
3. Correlate depth ({{correlation}}) — confirm setting depth
   {{depth}} m.

### 3.2 Set Packer

1. Close annulus; pressure up tubing gradually:
   - 500 psi → hold 5 min (check for leaks)
   - 1000 psi → 1500 psi → {{set_pressure}} psi (shear at
     {{shear_pressure}} psi)
2. Hold {{set_pressure}} psi for {{hold_time}} min.
3. Bleed to zero — confirm weight change (set).
4. Overpull {{overpull}} klbs to confirm packer set.

### 3.3 Test

1. Test from annulus: {{test_pressure}} psi, hold 15 min —
   acceptance: no more than {{leak_tolerance}} psi drop.
2. Test tubing string against plug/seal: {{tubing_test}} psi,
   15 min.
3. Record all pressures on test form; sign off.

## 4. HOLD POINT

> **HP:** Packer set and tested ({{test_pressure}} psi annulus) —
> witnessed by Company Supervisor + Client.

## 5. CONTINGENCIES

- **Packer not set (no weight change):** re-cycle pressure, check
  shear; if fails — retrieve and redress.
- **Leak at packer:** re-set with higher pressure; if still leaking —
  POOH, inspect, replace.
- **Cannot get to depth:** drift/cleanout first; do not force.

## 6. HSE

- High-pressure operations — barricade; no personnel near pump truck
  lines.
- Communication pump operator ↔ driller ↔ supervisor.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

PACKER_SET_PROC.inputs += [
    InputSpec("line_test", "Line Test", "number", unit="psi", default="5000",
              group="Packer"),
    InputSpec("rih_speed", "Max RIH Speed", "number", unit="m/min",
              default="10", group="Packer"),
    InputSpec("correlation", "Depth Correlation", "text",
              placeholder="e.g. GR/CCL run", group="Packer"),
    InputSpec("hold_time", "Hold at Set Pressure", "number", unit="min",
              default="15", group="Packer"),
    InputSpec("overpull", "Overpull to Confirm", "number", unit="klbs",
              default="10", group="Packer"),
    InputSpec("leak_tolerance", "Leak Tolerance", "number", unit="psi",
              default="50", group="Packer"),
    InputSpec("tubing_test", "Tubing Test Pressure", "number", unit="psi",
              default="3500", group="Packer"),
]

# 9. PERFORATION PROCEDURE (WIRELINE)
PERFORATION_PROC = TemplateDef(
    key="perforation_procedure",
    name="Perforation Procedure (Wireline / TCP)",
    icon="🎯",
    kind="Procedure",
    description="Perforation procedure: gun selection, depth control, "
                "underbalance, firing, verification and well control.",
    inputs=_well_inputs() + [
        InputSpec("interval", "Perforation Interval", "text", required=True,
                  placeholder="e.g. 2450-2465 m MD", group="Perf"),
        InputSpec("method", "Method", "combo",
                  options=["Wireline (E-line)", "Tubing Conveyed (TCP)",
                           "Coiled Tubing"], group="Perf"),
        InputSpec("gun", "Gun Type", "text",
                  placeholder="e.g. 2-7/8\" HMX 6 spf", group="Perf"),
        InputSpec("underbalance", "Underbalance", "number", unit="psi",
                  default="300", group="Perf"),
        InputSpec("fluid", "Well Fluid", "text", placeholder="e.g. brine 9.0 ppg",
                  group="Perf"),
    ],
    markdown=r"""
# PERFORATION PROCEDURE ({{method}}) — {{well_name}}

**Field:** {{field}} | **Rig/Unit:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Perforate interval **{{interval}}** in well **{{well_name}}** using
**{{method}}** with **{{gun}}**, with an underbalance of
{{underbalance}} psi, safely and with accurate depth control.

## 2. PRE-JOB CHECKLIST

- [ ] Gun inspected and certified; charges dated within shelf life
- [ ] Depth control: correlation log available ({{correlation}})
- [ ] Well filled with {{fluid}}; fluid level confirmed
- [ ] BOP / lubricator sized and tested ({{bop_test}} psi)
- [ ] Firing head function tested; safety pin in place until ready
- [ ] Underbalance plan agreed ({{underbalance}} psi)
- [ ] H2S / gas monitoring active ({{h2s}})

## 3. PROCEDURE

### 3.1 Rig-Up

1. Rig up lubricator / BOP; pressure test {{bop_test}} psi.
2. Make up gun string: {{gun_string}}.
3. Function test firing head and correlation tool.

### 3.2 Depth Control

1. RIH to {{interval}}.
2. Run correlation log (GR/CCL) — correlate against
   {{correlation_ref}}.
3. Space out guns on depth; lock depth with casing collar.

### 3.3 Fire

1. Set underbalance: bleed fluid level / N2 lift as planned.
2. Arm firing head (remove safety pin) per procedure.
3. **Fire** — confirm detonation (surface indication / gauge).
4. Verify with post-run (temperature/radioactive tag) if required:
   {{verification}}.

### 3.4 Post-Perforation

1. POOH guns; inspect; count charges (all fired:
   {{charges_fired}}/{{charges_total}}).
2. Observe well: flow / fill-up / H2S.
3. Rig down; record final wellhead pressure.

## 4. WELL CONTROL

- If well flows after perforation: shut in per procedure, inform
  supervisor.
- H2S watch during flowback ({{h2s}}).
- Flare/separator lined up if flow expected ({{flow_expected}}).

## 5. HOLD POINT

> **HP:** Guns on depth and firing approved by Company Supervisor +
> perforating service supervisor.

## 6. CONTINGENCIES

- **No detonation:** POOH, inspect, re-run per procedure.
- **Partial detonation:** verify with correlation, re-run if needed.
- **Guns stuck:** work line, jar; fishing plan if required.

## 7. HSE

- Explosives handling: certified personnel, no radio transmission during
  run, magazine log maintained.
- Barricade area; no hot work near explosives.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

PERFORATION_PROC.inputs += [
    InputSpec("correlation", "Correlation Tool", "text",
              placeholder="e.g. GR/CCL", group="Perf"),
    InputSpec("correlation_ref", "Correlation Reference", "text",
              placeholder="e.g. 9-5/8\" shoe @ 2350m", group="Perf"),
    InputSpec("bop_test", "BOP/Lubricator Test", "number", unit="psi",
              default="5000", group="Perf"),
    InputSpec("gun_string", "Gun String", "text",
              placeholder="e.g. cable head + CCL + firing head + gun",
              group="Perf"),
    InputSpec("verification", "Post-Run Verification", "text",
              placeholder="e.g. radioactive tag / gauge data",
              group="Perf"),
    InputSpec("charges_fired", "Charges Fired", "number", group="Perf"),
    InputSpec("charges_total", "Charges Total", "number", group="Perf"),
    InputSpec("flow_expected", "Flow Expected", "combo", options=["YES", "NO"],
              group="Perf"),
]

# 10. DST PROCEDURE
DST_PROC = TemplateDef(
    key="dst_procedure",
    name="DST Procedure (Drill Stem Test)",
    icon="🧪",
    kind="Procedure",
    description="DST procedure: test string, tool function, flow periods, "
                "shut-in, gauges, sampling and interpretation interface.",
    inputs=_well_inputs() + [
        InputSpec("interval", "Test Interval", "text", required=True,
                  group="DST"),
        InputSpec("tools", "DST Tools", "text",
                  placeholder="e.g. RTTS + tester valve + bypass + jars + gauges",
                  group="DST"),
        InputSpec("flow_period", "Flow Period", "number", unit="hrs",
                  default="4", group="DST"),
        InputSpec("bu_period", "Build-up Period", "number", unit="hrs",
                  default="12", group="DST"),
        InputSpec("gauges", "Gauges", "text",
                  placeholder="e.g. 2 x quartz + 2 x memory", group="DST"),
    ],
    markdown=r"""
# DRILL STEM TEST PROCEDURE — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Test interval **{{interval}}** in well **{{well_name}}** by DST to
determine flow potential, reservoir pressure, permeability and to obtain
fluid samples.

## 2. TEST STRING & TOOLS

| Item | Specification |
|---|---|
| Packer | {{packer}} |
| Tester valve | {{tester_valve}} |
| Bypass / circulating valve | {{bypass}} |
| Jars | {{jars}} |
| Gauges | {{gauges}} |
| Sampling tools | {{samplers}} |
| String | {{string}} |

- Tools function tested at surface before RIH.
- Gauges programmed and synchronized ({{gauge_program}}).

## 3. PROCEDURE

### 3.1 RIH

1. RIH test string slowly; fill per plan; monitor.
2. Set packer at {{packer_depth}} m; test packer
   ({{packer_test}} psi).
3. Open tester valve — **initial flow** (clean-up): {{cleanup_period}}
   hrs.

### 3.2 Flow & Shut-in Sequence

1. **Flow #1:** {{flow_period}} hrs through {{choke}} choke.
2. **Shut-in #1 (ISIP):** {{isip}} hrs.
3. **Flow #2:** {{flow_period_2}} hrs.
4. **Final shut-in (BU):** {{bu_period}} hrs.
5. Circulate out through bypass; close in; retrieve samples.

### 3.3 Sampling

- Oil: {{oil_samples}} — at surface + downhole ({{sample_tools}}).
- Gas: {{gas_samples}}.
- Water: {{water_samples}}.

### 3.4 POOH

1. Unset packer; POOH test string carefully.
2. Rig down; download gauges.
3. Deliver preliminary interpretation within {{prelim_days}} days.

## 4. DATA RECORDING

| Period | Duration | Choke | Rate | WHP | Remarks |
|---|---|---|---|---|---|

## 5. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | RIH | Tools tested; packer set |
| HP-02 | Flow | Initial flow reviewed |
| HP-03 | BU | Build-up completed |

## 6. CONTINGENCIES

- **Tools stuck:** jar, back-off, fishing.
- **No flow:** nitrogen lift / swabbing if planned; evaluate.
- **High H2S:** terminate test, circulate out, shut in per plan.

## 7. HSE

- Flare/burner permit; wind sock; no-fly zone.
- H2S continuous monitoring ({{h2s}}).
- Emergency shutdown tested before flow.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

DST_PROC.inputs += [
    InputSpec("packer", "Packer", "text", placeholder="e.g. RTTS 9-5/8\"",
              group="DST"),
    InputSpec("tester_valve", "Tester Valve", "text",
              placeholder="e.g. APR ball valve", group="DST"),
    InputSpec("bypass", "Bypass / Circulating Valve", "text", group="DST"),
    InputSpec("jars", "Jars", "text", group="DST"),
    InputSpec("samplers", "Sampling Tools", "text",
              placeholder="e.g. RFT / single-phase samplers", group="DST"),
    InputSpec("string", "String", "text", placeholder="e.g. 5\" DP",
              group="DST"),
    InputSpec("gauge_program", "Gauge Program", "text",
              placeholder="e.g. 1 sec sampling, 15K psi", group="DST"),
    InputSpec("packer_depth", "Packer Depth", "number", unit="m",
              group="DST"),
    InputSpec("packer_test", "Packer Test", "number", unit="psi",
              default="3000", group="DST"),
    InputSpec("cleanup_period", "Clean-up Flow", "number", unit="hrs",
              default="1", group="DST"),
    InputSpec("choke", "Flow Choke", "text", placeholder="e.g. 24/64\"",
              group="DST"),
    InputSpec("flow_period_2", "Flow #2 Duration", "number", unit="hrs",
              default="6", group="DST"),
    InputSpec("isip", "ISIP Duration", "number", unit="hrs", default="1",
              group="DST"),
    InputSpec("oil_samples", "Oil Samples", "text", group="Samples"),
    InputSpec("gas_samples", "Gas Samples", "text", group="Samples"),
    InputSpec("water_samples", "Water Samples", "text", group="Samples"),
    InputSpec("sample_tools", "Sample Tools", "text", group="Samples"),
    InputSpec("prelim_days", "Preliminary Report", "number", unit="days",
              default="3", group="Report"),
]

# 11. WELLHEAD INSTALLATION PROCEDURE
WELLHEAD_PROC = TemplateDef(
    key="wellhead_installation_procedure",
    name="Wellhead Installation Procedure (THS/THA/XMT)",
    icon="🏗️",
    kind="Procedure",
    description="Wellhead (THS / THA / XMT) installation and pressure test "
                "procedure with P-seal and ring gasket requirements.",
    inputs=_well_inputs() + [
        InputSpec("wellhead_type", "Wellhead Type", "text", required=True,
                  placeholder="e.g. ESP THS 13-5/8\" x 11\" 5K + THA + XMT",
                  group="WH"),
        InputSpec("vendor", "Wellhead Vendor", "text", group="WH"),
        InputSpec("p_seal_test", "P-Seal Test", "number", unit="psi",
                  default="4000", group="WH"),
        InputSpec("body_test", "Body/Valve Test", "number", unit="psi",
                  default="4500", group="WH"),
        InputSpec("ring_gaskets", "Ring Gaskets", "text",
                  placeholder="e.g. BX-160, RX-39", group="WH"),
    ],
    markdown=r"""
# WELLHEAD INSTALLATION PROCEDURE — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Vendor:** {{vendor}}
**Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Install / replace the wellhead equipment (**{{wellhead_type}}**) on well
**{{well_name}}** with correct make-up, P-seals and ring gaskets, and
verify integrity by pressure testing.

## 2. PRE-JOB CHECKLIST

- [ ] Drawings and OEM procedures available
- [ ] Ring gaskets confirmed ({{ring_gaskets}}) — correct type/size
- [ ] P-seal ports open and testable
- [ ] Studs, nuts and tie-down screws free and anti-seized
- [ ] Bolt circles match between components
- [ ] Lifting equipment certified; rigging plan approved
- [ ] Penetrator rod / exit blocks verified ({{penetrator_check}})
- [ ] H2S watch ({{h2s}})

## 3. PROCEDURE

### 3.1 Prepare

1. Inspect casing neck / spool hub seal surfaces (no cuts, corrosion).
2. Clean and dress seal surfaces; install new ring gasket
   ({{ring_gasket_size}}).
3. Pre-fit components at surface/workshop where possible.

### 3.2 Install THS

1. Lift and land THS on the casing head; align bolt holes.
2. Make up studs evenly to {{stud_torque}} ft-lbs (cross pattern).
3. Inject P-seal packing compound; test P-seal zones
   ({{p_seal_test}} psi, 15 min).
4. Test body and side outlets: {{body_test}} psi, 15 min.

### 3.3 Install THA

1. Verify penetrator rod passes through THA ({{penetrator_check}}).
2. Orient THA per drawing; route control lines through exit blocks.
3. Land THA; tighten studs; inject P-seals; test
   {{p_seal_test}} psi.

### 3.4 Install XMT

1. Land XMT on THA with new ring gasket.
2. Make up studs to {{stud_torque}} ft-lbs.
3. Test XMT body and valves: {{body_test}} psi, 15 min.
4. Function test all valves (open/close).

## 4. TEST MATRIX

| Item | Pressure (psi) | Hold (min) | Acceptance |
|---|---|---|---|
| P-seal zones | {{p_seal_test}} | 15 | No leak |
| THS body / outlets | {{body_test}} | 15 | No leak |
| THA P-seals | {{p_seal_test}} | 15 | No leak |
| XMT body / valves | {{body_test}} | 15 | No leak |

## 5. HOLD POINT

> **HP:** Wellhead installed and tested — witnessed by Company Supervisor
> + wellhead engineer + Client.

## 6. CONTINGENCIES

- **Leak at P-seal:** re-inject compound, re-test; if persists —
  investigate port/gasket.
- **Gasket leak:** bleed, replace gasket, re-make, re-test.
- **Bolt hole mismatch:** measure and verify against drawing; stop if
  mismatch — do not force.

## 7. HSE

- Heavy lifts: certified slings, rigger in charge, barricade.
- High-pressure test: no personnel near wellhead during test.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

WELLHEAD_PROC.inputs += [
    InputSpec("penetrator_check", "Penetrator Rod Check", "combo",
              options=["OK - passes", "Needs machining", "N/A"],
              group="WH"),
    InputSpec("ring_gasket_size", "Ring Gasket Installed", "text",
              group="WH"),
    InputSpec("stud_torque", "Stud Torque", "text",
              placeholder="e.g. 450 ft-lbs", group="WH"),
]

# 12. LOST CIRCULATION TREATMENT PROCEDURE
LOST_CIRC_PROC = TemplateDef(
    key="lost_circulation_procedure",
    name="Lost Circulation Treatment Procedure",
    icon="🕳️",
    kind="Procedure",
    description="Lost circulation detection, classification, LCM pills, "
                "balanced plugs, cement plugs and evaluation.",
    inputs=_well_inputs() + [
        InputSpec("rate_loss", "Loss Rate", "text", required=True,
                  placeholder="e.g. 50 bbl/hr", group="LC"),
        InputSpec("zone", "Loss Zone (depth)", "text", group="LC"),
        InputSpec("mud_weight", "Mud Weight", "number", unit="ppg",
                  group="LC"),
        InputSpec("fg", "Fracture Gradient at Zone", "number", unit="ppg",
                  group="LC"),
    ],
    markdown=r"""
# LOST CIRCULATION TREATMENT PROCEDURE — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Detect, classify and cure lost circulation in well **{{well_name}}**
(loss rate {{rate_loss}} at {{zone}}) while protecting the reservoir
and maintaining well control.

## 2. DETECTION & CLASSIFICATION

| Severity | Loss Rate | Typical Action |
|---|---|---|
| Seepage | < 10 bbl/hr | LCM pill, continue |
| Partial | 10-50 bbl/hr | LCM pills, reduce MW, plug |
| Severe | > 50 bbl/hr | Balanced plug / cement, evaluate |
| Total | No returns | Stop, plug, evaluate |

- Monitor pit volume, flow-out, trip tank — record every
  {{monitor_interval}} min.
- Confirm zone from drilling break, ROP change, cuttings, LWD
  ({{confirmation}}).

## 3. TREATMENT SEQUENCE

### 3.1 Immediate Actions

1. Stop drilling; pick up off bottom.
2. Fill hole continuously to maintain hydrostatic
   (keep {{fill_fluid}}).
3. Reduce pump rate / stop pumps; observe.

### 3.2 LCM Pills

1. Spot hi-vis LCM pill: {{lcm_type}}
   (concentration {{lcm_concentration}} ppb, volume {{lcm_volume}} bbl).
2. Squeeze slowly ({{squeeze_rate}} bpm) — do not exceed
   {{max_squeeze_pressure}} psi.
3. Soak {{soak_time}} min; test returns.

### 3.3 Reduce Mud Weight / Plug

1. If losses continue: reduce MW by {{mw_reduction}} ppg
   (verify against pore pressure — min {{min_mw}} ppg).
2. If still no cure: set balanced plug
   ({{plug_type}}, {{plug_volume}} bbl) across
   {{zone}}.
3. WOC {{woc_time}} hrs; tag and test.

### 3.4 Cement Plug (if required)

1. Set cement plug per cementing program ({{cement_program}}).
2. Tag, pressure test {{plug_test}} psi.
3. Resume drilling at reduced parameters
   ({{resume_params}}).

## 4. MONITORING AFTER TREATMENT

- [ ] Pit volume stable over {{monitor_time}} hrs
- [ ] Flow-out normal; no losses while circulating
- [ ] ECD within limits (max {{ecd_max}} ppg)
- [ ] Record all volumes on the loss report

## 5. HOLD POINT

> **HP:** Losses cured (pit volume stable) — confirmed by Company
> Supervisor before drilling ahead.

## 6. CONTINGENCIES

- **Total losses with gas zone:** keep hole full, activate well control
  plan, consider heavier fluid if kick risk.
- **No cure after 2 pills:** escalate — cement plug / casing point
  decision with office.

## 7. HSE

- Keep rig floor clear; monitor gas/H2S ({{h2s}}).
- LCM mixing: dust control, PPE.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

LOST_CIRC_PROC.inputs += [
    InputSpec("monitor_interval", "Monitor Interval", "number", unit="min",
              default="15", group="LC"),
    InputSpec("confirmation", "Zone Confirmation", "text",
              placeholder="e.g. drilling break + cuttings change",
              group="LC"),
    InputSpec("fill_fluid", "Fill Fluid", "text", default="mud from pits",
              group="LC"),
    InputSpec("lcm_type", "LCM Type", "combo",
              options=["Fine/medium (10-30 ppb)", "Coarse (30-60 ppb)",
                       "Hi-vis + fiber", "Gunk squeeze"],
              group="LCM"),
    InputSpec("lcm_concentration", "LCM Concentration", "number", unit="ppb",
              default="30", group="LCM"),
    InputSpec("lcm_volume", "LCM Pill Volume", "number", unit="bbl",
              default="50", group="LCM"),
    InputSpec("squeeze_rate", "Squeeze Rate", "number", unit="bpm",
              default="2", group="LCM"),
    InputSpec("max_squeeze_pressure", "Max Squeeze Pressure", "number",
              unit="psi", group="LCM"),
    InputSpec("soak_time", "Soak Time", "number", unit="min", default="30",
              group="LCM"),
    InputSpec("mw_reduction", "MW Reduction", "number", unit="ppg",
              group="Plug"),
    InputSpec("min_mw", "Minimum Safe MW", "number", unit="ppg",
              group="Plug"),
    InputSpec("plug_type", "Plug Type", "combo",
              options=["Balanced bentonite plug", "Gunk plug",
                       "Cement plug"], group="Plug"),
    InputSpec("plug_volume", "Plug Volume", "number", unit="bbl",
              group="Plug"),
    InputSpec("woc_time", "WOC Time", "number", unit="hrs", default="12",
              group="Plug"),
    InputSpec("plug_test", "Plug Test Pressure", "number", unit="psi",
              default="500", group="Plug"),
    InputSpec("cement_program", "Cement Program Ref", "text",
              placeholder="e.g. see cementing program CP-02",
              group="Plug"),
    InputSpec("resume_params", "Resume Parameters", "text",
              placeholder="e.g. WOB 10k, RPM 80, 600 gpm",
              group="Plug"),
    InputSpec("monitor_time", "Stability Monitoring", "number", unit="hrs",
              default="4", group="Plug"),
    InputSpec("ecd_max", "Max ECD", "number", unit="ppg", group="Plug"),
]

# 13. RIG MOVE & RIG-UP PROCEDURE
RIG_MOVE_PROC = TemplateDef(
    key="rig_move_procedure",
    name="Rig Move & Rig-Up Procedure",
    icon="🚛",
    kind="Procedure",
    description="Rig move, rig-up, leveling, safety checks and spud "
                "preparation procedure.",
    inputs=_well_inputs() + [
        InputSpec("rig_type", "Rig Type", "text",
                  placeholder="e.g. 1000 HP truck mounted",
                  group="Move"),
        InputSpec("move_distance", "Move Distance", "number", unit="km",
                  group="Move"),
        InputSpec("duration", "Planned Duration", "number", unit="days",
                  group="Move"),
    ],
    markdown=r"""
# RIG MOVE & RIG-UP PROCEDURE — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig_type}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Move rig **{{rig_type}}** to well **{{well_name}}** location
({{move_distance}} km), rig up, level and prepare for operations safely
within {{duration}} days.

## 2. PRE-MOVE CHECKLIST

- [ ] Location survey and access road checked
- [ ] Permits (road, transport, location) obtained
- [ ] Heavy-lift and transport plan approved
- [ ] Crew transport arranged; HSE induction done
- [ ] Load-out sequence agreed with rig mover

## 3. MOVE & RIG-UP

### 3.1 Load-Out / Transport

1. Secure all loads; weight certificates verified.
2. Escort/pilot vehicles per local regulation.
3. Speed limits and convoy rules enforced.

### 3.2 Rig-Up

1. Position rig per location drawing; set chocks.
2. **Level rig** — verify within tolerance
   ({{level_tolerance}} mm).
3. Rig up mast, substructure, BOP handling equipment.
4. Install and connect: power, mud system, air, water, fuel.
5. Test safety equipment: BOP, fire, gas detection, ESD.

### 3.3 Spud Preparation

1. Set conductor / cellar per plan ({{conductor}}).
2. Nipple up and test BOP ({{bop_test}} psi).
3. Calibrate instrumentation (weight indicator, gauges).
4. Line up mud system; test pumps.
5. Pre-spud safety meeting and inspection.

## 4. HOLD POINT

> **HP:** Rig-up complete, BOP tested, safety inspection passed — spud
> approved.

## 5. HSE

- Lifting plan with certified riggers; barricades.
- No lifting over personnel; hand signals/radio.
- Housekeeping and fire extinguishers in place.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

RIG_MOVE_PROC.inputs += [
    InputSpec("level_tolerance", "Level Tolerance", "number", unit="mm",
              default="5", group="Move"),
    InputSpec("conductor", "Conductor Plan", "text",
              placeholder="e.g. 30\" driven to 40m", group="Move"),
    InputSpec("bop_test", "BOP Test Pressure", "number", unit="psi",
              default="3000", group="Move"),
]

# 14. H2S EMERGENCY RESPONSE PROCEDURE
H2S_PROC = TemplateDef(
    key="h2s_emergency_procedure",
    name="H2S Emergency Response Procedure",
    icon="⚠️",
    kind="Procedure",
    description="H2S detection levels, alarms, response actions, escape "
                "routes, BA/SCBA and emergency plan.",
    inputs=_well_inputs() + [
        InputSpec("h2s_level", "Expected H2S Level", "text",
                  placeholder="e.g. up to 5%", group="H2S"),
        InputSpec("alarm_1", "Alarm Level 1", "number", unit="ppm",
                  default="10", group="H2S"),
        InputSpec("alarm_2", "Alarm Level 2", "number", unit="ppm",
                  default="20", group="H2S"),
        InputSpec("assembly", "Assembly Point", "text",
                  placeholder="e.g. upwind, 200m from well",
                  group="H2S"),
    ],
    markdown=r"""
# H2S EMERGENCY RESPONSE PROCEDURE — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Protect personnel, the public and the environment from hydrogen sulfide
(H2S, expected {{h2s_level}}) during operations on well **{{well_name}}**.

## 2. H2S PROPERTIES & HAZARDS

- Heavier than air — accumulates in low areas.
- Toxic at low concentrations; lethal above 100 ppm.
- Flammable; corrosive (NACE considerations).
- Odor: rotten eggs (but nose desensitizes quickly).

## 3. DETECTION & ALARMS

| Alarm | Level | Action |
|---|---|---|
| Level 1 (Alert) | {{alarm_1}} ppm | Continuous monitoring, don BA, no ignition |
| Level 2 (Alarm) | {{alarm_2}} ppm | Stop work, don BA/SCBA, evacuate non-essential |
| Level 3 (Emergency) | {{alarm_3}} ppm | Evacuate to assembly point, emergency plan |

- Fixed monitors at: rig floor, shale shakers, mud pits, choke manifold,
  living quarters.
- Portable monitors for all personnel; wind socks visible.

## 4. RESPONSE ACTIONS

### 4.1 Level 1

1. Alert all personnel; increase monitoring frequency.
2. Check wind direction; post wind socks.
3. Prepare BA/SCBA sets; no smoking / no ignition sources.

### 4.2 Level 2

1. Sound alarm; stop non-essential work.
2. All personnel don BA/SCBA.
3. Move upwind to assembly point **{{assembly}}**.
4. Shut in well if H2S from well (per well control procedure).

### 4.3 Level 3

1. Evacuate to assembly point; head count.
2. Activate emergency response: contact {{emergency_contact}}.
3. Only trained rescue team with BA enters affected areas.
4. Monitor from safe distance until gas dissipates.

## 5. DRILLS & EQUIPMENT

- H2S drill frequency: {{drill_freq}}.
- BA/SCBA inspection: {{ba_inspection}} (weekly).
- Number of BA sets on location: {{ba_sets}} (+{{ba_extra}} spare).
- Medical: oxygen, first aid trained personnel
  ({{medical}}).

## 6. HOLD POINT

> **HP:** H2S equipment inspected and drill completed before opening
> the well / before operations.

## 7. POST-EVENT

1. Confirm H2S below alarm level before re-entry.
2. Debrief; report per company procedure.
3. Restore and re-inspect equipment.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

H2S_PROC.inputs += [
    InputSpec("alarm_3", "Alarm Level 3", "number", unit="ppm", default="100",
              group="H2S"),
    InputSpec("emergency_contact", "Emergency Contact", "text",
              group="H2S"),
    InputSpec("drill_freq", "Drill Frequency", "combo",
              options=["Weekly", "Monthly", "Quarterly"],
              group="H2S"),
    InputSpec("ba_inspection", "BA Inspection Frequency", "combo",
              options=["Weekly", "Monthly"], group="H2S"),
    InputSpec("ba_sets", "BA Sets on Location", "number", default="6",
              group="H2S"),
    InputSpec("ba_extra", "Spare BA Sets", "number", default="2",
              group="H2S"),
    InputSpec("medical", "Medical Arrangements", "text",
              placeholder="e.g. clinic + oxygen + trained medics",
              group="H2S"),
]

# 15. TUBING PRESSURE TEST PROCEDURE
TUBING_TEST_PROC = TemplateDef(
    key="tubing_pressure_test_procedure",
    name="Tubing Pressure Test Procedure",
    icon="🧪",
    kind="Procedure",
    description="Completion string pressure test procedure: setup, test "
                "sequence, acceptance criteria and leak troubleshooting.",
    inputs=_well_inputs() + [
        InputSpec("string", "String Description", "text",
                  placeholder="e.g. 4-1/2\" 18.9# L-80 VAM TOP",
                  group="Test"),
        InputSpec("test_pressure", "Test Pressure", "number", unit="psi",
                  default="4500", group="Test"),
        InputSpec("hold_time", "Hold Time", "number", unit="min", default="15",
                  group="Test"),
        InputSpec("leak_tolerance", "Acceptance (leak)", "number", unit="psi",
                  default="50", group="Test"),
        InputSpec("plug_depth", "Plug Depth", "number", unit="m",
                  group="Test"),
    ],
    markdown=r"""
# TUBING PRESSURE TEST PROCEDURE — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Pressure test the completion string (**{{string}}**) in well
**{{well_name}}** to {{test_pressure}} psi against a plug at
{{plug_depth}} m to verify thread/connection integrity.

## 2. PRE-TEST CHECKLIST

- [ ] Plug ({{plug_type}}) set and depth confirmed
- [ ] Test line rigged from pump to tree; tested
  ({{line_test}} psi)
- [ ] Pressure gauge calibrated ({{gauge}})
- [ ] All personnel clear of test area
- [ ] H2S watch ({{h2s}})

## 3. PROCEDURE

1. Rig up pump and lines; pressure test lines to {{line_test}} psi.
2. Close tree valves as required; open test port.
3. Pump slowly into tubing — monitor volume vs pressure
   ({{volume_pressure}}).
4. Pressure up in steps: 500 → 1500 → {{test_pressure}} psi
   (hold 5 min at each intermediate step).
5. Hold {{test_pressure}} psi for {{hold_time}} min.
6. **Acceptance:** pressure drop ≤ {{leak_tolerance}} psi.
7. Bleed down gradually; record final data on test form.

## 4. TROUBLESHOOTING

| Symptom | Likely Cause | Action |
|---|---|---|
| Fast drop | Connection leak | Re-torque, re-test |
| Slow drop | Valve/plug leak | Isolate, check plug, check valves |
| No pressure build | Open path | Check plug depth / circulation path |

- Never exceed test pressure; never pump against closed system without
  relief.

## 5. HOLD POINT

> **HP:** Test accepted (≤ {{leak_tolerance}} psi drop) — witnessed by
> Company Supervisor.

## 6. HSE

- High-pressure test: barricade, signs, communication.
- No personnel near tree during test.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

TUBING_TEST_PROC.inputs += [
    InputSpec("plug_type", "Plug Type", "text",
              placeholder="e.g. 2.750\" SSD plug", group="Test"),
    InputSpec("line_test", "Line Test", "number", unit="psi", default="5000",
              group="Test"),
    InputSpec("gauge", "Gauge", "text",
              placeholder="e.g. 0-10K psi certified", group="Test"),
    InputSpec("volume_pressure", "Volume/Pressure Check", "combo",
              options=["YES", "NO"], group="Test"),
]

# 16. DRILLSTRING MAKE-UP (BHA) PROCEDURE
BHA_PROC = TemplateDef(
    key="bha_makeup_procedure",
    name="BHA Make-Up Procedure",
    icon="⚙️",
    kind="Procedure",
    description="BHA assembly and make-up: inspection, torque, function "
                "tests, handling and RIH.",
    inputs=_well_inputs() + [
        InputSpec("bha_desc", "BHA Description", "textarea", required=True,
                  placeholder="e.g. bit 12-1/4\" PDC + motor 9-5/8\" + MWD + DC x6",
                  group="BHA"),
        InputSpec("torque", "Make-Up Torque", "text",
                  placeholder="e.g. 35,000 ft-lbs optimum",
                  group="BHA"),
        InputSpec("bit_size", "Bit Size", "number", unit="in",
                  group="BHA"),
    ],
    markdown=r"""
# BHA MAKE-UP PROCEDURE — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. OBJECTIVE

Assemble the BHA (**{{bha_desc}}**) for well **{{well_name}}** correctly
— torque, function tests, handling — and run in hole without damage.

## 2. PRE-MAKE-UP CHECKLIST

- [ ] All components inspected (threads, seals, OD/ID)
- [ ] Torque gauge calibrated (range covers {{torque}})
- [ ] Tongs, elevators, slips sized correctly
- [ ] Bit inspected; nozzles installed per hydraulics
  ({{nozzles}})
- [ ] Motor / RSS / MWD function tested ({{function_test}})
- [ ] BHA components drifted (ID check)
- [ ] Safety meeting with crew

## 3. PROCEDURE

### 3.1 Bit

1. Inspect bit ({{bit_type}}); verify nozzle sizes
   ({{nozzles}}).
2. Make up bit to first stabilizer/bit sub at {{bit_torque}} ft-lbs.

### 3.2 BHA Components

1. Lay out components in order per tally.
2. Make up each connection at OEM torque
   ({{torque}}), using correct dope.
3. Record torque-turn on each connection.
4. Function test motor/RSS/MWD after make-up
   ({{function_test}}).

### 3.3 RIH

1. RIH BHA slowly (max {{rih_speed}} m/min).
2. Fill string per plan; monitor drag.
3. At casing shoe: stop, check, continue per program.

## 4. HOLD POINT

> **HP:** BHA made up and function tested — accepted before RIH.

## 5. CONTINGENCIES

- **Connection leak/cross-thread:** back off, inspect, re-make.
- **Motor test failure:** replace motor, re-test.
- **Tool dropped:** fishing plan immediately.

## 6. HSE

- Handling of long BHA: use correct lifts; no personnel under load.
- Tongs guarded; communication driller – floor crew.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

BHA_PROC.inputs += [
    InputSpec("nozzles", "Nozzles / TFA", "text",
              placeholder="e.g. 5x16 (0.98 sq.in)", group="BHA"),
    InputSpec("bit_type", "Bit Type", "text", placeholder="e.g. PDC",
              group="BHA"),
    InputSpec("bit_torque", "Bit Make-Up Torque", "text",
              placeholder="e.g. 12,000 ft-lbs", group="BHA"),
    InputSpec("function_test", "Function Test", "text",
              placeholder="e.g. motor pressure test @ 300 gpm",
              group="BHA"),
    InputSpec("rih_speed", "Max RIH Speed", "number", unit="m/min",
              default="10", group="BHA"),
]

# ----------------------------------------------------------------------------
# 17. CASING RUNNING & CEMENTING PROCEDURE (REAL FIELD STYLE)
# ----------------------------------------------------------------------------
# Based on the real field document "13 3/8 x 13 5/8 Casing Running &
# Cementing Procedure - E001S" (library #001) — 26-item casing checklist
# and 32-item cementing checklist with distribution and preparation notes.
# ----------------------------------------------------------------------------

CASING_CEMENT_PROC = TemplateDef(
    key="casing_running_cementing_procedure",
    name="Casing Running & Cementing Procedure (Field style)",
    icon="🏗️",
    kind="Procedure",
    description=(
        "Real field procedure (E001S style): distribution, "
        "26-item casing-running checklist, 32-item cementing checklist, "
        "preparation before job, operation sequences and HSE."),
    inputs=_well_inputs() + [
        InputSpec("casing_size", "Casing Size", "text", required=True,
                  placeholder="e.g. 13-3/8\" x 13-5/8\"",
                  group="Casing"),
        InputSpec("casing_depth", "Casing Depth", "number", unit="m",
                  group="Casing"),
        InputSpec("shoe_size", "Shoe / Collar", "text",
                  placeholder="e.g. 13-3/8\" float shoe + float collar",
                  group="Casing"),
        InputSpec("centralizers", "Centralizers", "text",
                  placeholder="e.g. bow-spring, 2 per joint",
                  group="Casing"),
        InputSpec("connection", "Connection", "text",
                  placeholder="e.g. BTC", group="Casing"),
        InputSpec("running_speed", "Running Speed (slips-to-slips)", "text",
                  placeholder="e.g. 60-90 sec/joint", group="Casing"),
        InputSpec("fill_volume", "Fill-Up Volume", "number", unit="bbl/jt",
                  group="Casing"),
        InputSpec("cement_head", "Cement Head", "text",
                  placeholder="e.g. 5K quick release", group="Cement"),
        InputSpec("slurry", "Slurry Design", "text",
                  placeholder="e.g. Class G 118 pcf + additives",
                  group="Cement"),
        InputSpec("slurry_volume", "Slurry Volume", "number", unit="bbl",
                  group="Cement"),
        InputSpec("displacement", "Displacement Volume", "number", unit="bbl",
                  group="Cement"),
        InputSpec("plug_set", "Plug Set", "text",
                  placeholder="e.g. top + bottom wiper plugs",
                  group="Cement"),
        InputSpec("cement_units", "Cement Units", "text",
                  placeholder="e.g. 2 operational + 1 standby",
                  group="Cement"),
        InputSpec("line_test", "Line Test Pressure", "number", unit="psi",
                  default="3000", group="Cement"),
        InputSpec("woc", "WOC Time", "number", unit="hrs", default="12",
                  group="Cement"),
        InputSpec("shoe_test", "Shoe Test Pressure", "number", unit="psi",
                  default="2500", group="Cement"),
        InputSpec("kick_assembly", "Kick Assembly", "text",
                  placeholder="e.g. X.O.S + FOSV (open)",
                  group="Well Control"),
    ],
    markdown=r"""
# CASING RUNNING & CEMENTING PROCEDURE — {{casing_size}} — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## DISTRIBUTION

| Role | | Role | |
|---|---|---|---|
| {{well_name}} WSS | | CSG Crew | | H2S Supervisor | | Geologist |
| Operator WSS | | Mud Logging | | HSE | | Waste Management |
| Tool Pusher | | Mud Engineer | | Cement Engineer | | |

> **Objective:** {{casing_size}} casing running & cementing procedure for
> well {{well_name}} to {{casing_depth}} m — safely, per program, with
> zero HSE incidents.

## CASING RUNNING CHECKLIST (26 items — filled by Wellsite Supervisor)

| # | Item | ✓ |
|---|---|---|
| 1 | HSE issues superior to any other issues; PJSM before each job | ☐ |
| 2 | All personnel involved have proper PPE | ☐ |
| 3 | Separate safety meeting with all participants; this document presented | ☐ |
| 4 | Inspection surveys on rig components; drilling lines checked | ☐ |
| 5 | Casing running equipment rigged up at appropriate time | ☐ |
| 6 | Casing tally and centralizer tally space-out checked; threads & centralizers checked | ☐ |
| 7 | All casing connections cleaned; all joints drifted | ☐ |
| 8 | Enough sealing compound (casing dope) and thread-lock compound available | ☐ |
| 9 | Shoe and collar joints visually inspected for debris | ☐ |
| 10 | Hot work permit mandatory in case of casing cut or welding | ☐ |
| 11 | Cut, bevel and welding equipment available for nipple-up wellhead | ☐ |
| 12 | Thread protectors removed; pin and box ends cleaned thoroughly | ☐ |
| 13 | Casing running service equipment checked with spare parts | ☐ |
| 14 | All safety features functioning on power tongs | ☐ |
| 15 | Maximum pull information available at rig floor | ☐ |
| 16 | WSS specifies slips-to-slips running speed ({{running_speed}}) | ☐ |
| 17 | Correct nails for centralizers available | ☐ |
| 18 | Back-up running equipment checked out and function tested | ☐ |
| 19 | Centralizers, top & bottom plug, cement head, circulation swage available | ☐ |
| 20 | Power tong jaws suitable for {{casing_size}} casing | ☐ |
| 21 | Cement trucks prepared (2 operational + 1 standby) and chemicals available | ☐ |
| 22 | Shoe cleaned; float inspected for debris; flow-through tested | ☐ |
| 23 | Kick assembly available: X.O.S + FOSV ({{kick_assembly}}) | ☐ |
| 24 | Plastic buckets on floor; fill-up hoses flushed and free of solids | ☐ |
| 25 | Contingency plans reviewed | ☐ |
| 26 | All casing measured on rack; tally sent to engineering office before job | ☐ |

## CEMENTING CHECKLIST (32 items — filled by Wellsite Supervisor)

| # | Item | ✓ |
|---|---|---|
| 1 | Pre-job safety meeting with all personnel | ☐ |
| 2 | HSE issues superior; PJSM before each job | ☐ |
| 3 | Proper PPE for all personnel | ☐ |
| 4 | Cement program received and checked | ☐ |
| 5 | Bulk cement & additives available per program | ☐ |
| 6 | Cellar jet pump installed and tested | ☐ |
| 7 | Samples of dry cement, additives and mix water taken | ☐ |
| 8 | Cement units inspected — weight gauge, barrel counter, pressure gauge, data acquisition | ☐ |
| 9 | Latest calibration certificate (max 6 months) per company policy | ☐ |
| 10 | Quantities and volumes checked by WSS + cementing operator; compare job duration with thickening time | ☐ |
| 11 | Winter time: cold weather procedure in place; air humidity for silo displacement | ☐ |
| 12 | Seals on cement manifold in good condition with backup | ☐ |
| 13 | Casing chain secured before starting job | ☐ |
| 14 | Fill-up hose at rotary table ready | ☐ |
| 15 | Bulk cement supply pressure 40 psi; silos have pressure relief valve | ☐ |
| 16 | Volume and material calculations and inventory checked | ☐ |
| 17 | Sampling and confirmation testing carried out | ☐ |
| 18 | Chemicals thoroughly mixed; final mix samples labeled and retained | ☐ |
| 19 | Cement truck, lines and rig pump checked operationally | ☐ |
| 20 | Leak test up to Lo-Torque valve on cement hose to {{line_test}} psi | ☐ |
| 21 | Solution tanks ready and cleaned | ☐ |
| 22 | T-Line on cement manifold | ☐ |
| 23 | Cement quality checked when draining (sack cement) | ☐ |
| 24 | Pit system and lines/valves checked for leakage | ☐ |
| 25 | Suction pit volume checked prior to displacement | ☐ |
| 26 | 30% back-up cement available in bulk tanks | ☐ |
| 27 | Area barricaded; night lighting with fuel tanks full — one man checks fuel each 2 hrs | ☐ |
| 28 | 100% back-up additives available | ☐ |
| 29 | Mud pump suction strainers checked and cleaned | ☐ |
| 30 | Mud logger informed before start mixing cement | ☐ |
| 31 | Mud engineer to monitor displacement for losses | ☐ |
| 32 | Isolated space prepared in coral pit for excess cement | ☐ |

## PREPARATION BEFORE JOB

- Use casing dope on box of each joint while on racks (avoid dropping brush
  inside casing).
- Prepare casing running requirements: drifts, circulation swage.
- Prepare spacer spool + BOP stack and related equipment; check BOP career
  performance before job.
- Call all related services (casing running crew, wellhead crew, pump truck)
  at the exact time.
- Pick up circulating head and cement head; place in corner of rig floor.
- Check stabbing board installation and readiness.
- When out of the hole: remove wear bushing, clear rig floor, change bails,
  rig up handling tools, install side-door elevator and spider slips
  (change to spider when enough casing weight).
- Prepare casing accessories on rig floor: X-overs, centralizers,
  circulation swages, nails, dope, thread-lock compound.
- Ensure hole is full; monitor fluid level.
- Kick assembly: X.O.S + FOSV for emergency conditions.

## CASING RUNNING & CEMENTING OPERATION SEQUENCE

### Running

1. RIH casing at slips-to-slips speed per WSS instruction
   ({{running_speed}}), monitored continuously.
2. Fill casing every joint / per plan ({{fill_volume}} bbl/jt).
3. Make up connections to torque with correct dope ({{connection}}).
4. Install centralizers per tally ({{centralizers}}).
5. On bottom: circulate ({{displacement}} bbl displacement volume) and
   condition hole until clean.

### Cementing

1. Rig up cement head ({{cement_head}}) with plug set
   ({{plug_set}}).
2. Pressure test lines to {{line_test}} psi.
3. Pump spacer, slurry ({{slurry_volume}} bbl of {{slurry}}) and displace
   per program.
4. Bump plug; hold; check backflow; WOC {{woc}} hrs.
5. Pressure test shoe to {{shoe_test}} psi, 15 min.
6. Nipple up wellhead; test wellhead per procedure.

## HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Before running | Checklists 1-26 completed and signed |
| HP-02 | Before cementing | Checklists 1-32 completed and signed |
| HP-03 | After cementing | Plug bumped; no backflow; shoe test accepted |

## CONTINGENCIES

- **Kick while running:** close BOP, use kick assembly
  ({{kick_assembly}}).
- **Losses while running:** keep hole full, LCM, reduce speed.
- **Lost returns during cement:** monitor, reduce rate, evaluate with
  office.
- **Cement unit failure:** switch to standby unit immediately.

## HSE

- HSE issues superior to any other issues — PJSM before each job.
- Hot work permit for cutting/welding.
- Barricade cement area; night lighting.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

# ----------------------------------------------------------------------------
# 18. CEMENT PLUG PROGRAM (REAL FIELD STYLE)
# ----------------------------------------------------------------------------
# Based on real field documents: SI#09 Cement Program Plug W120 MD850,
# Cementing Plug Program — general reference, etc.
# ----------------------------------------------------------------------------

CEMENT_PLUG_PROC = TemplateDef(
    key="cement_plug_procedure",
    name="Cement Plug Program (Field style)",
    icon="🧱",
    kind="Procedure",
    description=(
        "Real field cement plug program (SK/PECO-EN style): job "
        "design & calculations (plug length, slurry volume, spacer, "
        "displacement), slurry design with additives, job procedure, "
        "WOC, tag & test."),
    inputs=_well_inputs() + [
        InputSpec("plug_depth", "Plug Depth (MD)", "number", unit="m",
                  required=True, group="Design"),
        InputSpec("plug_length", "Plug Length", "number", unit="m",
                  default="115", group="Design"),
        InputSpec("hole_size", "Hole Size", "number", unit="in",
                  group="Design"),
        InputSpec("string", "String", "text",
                  placeholder="e.g. 5\" DP (ID 4.276\")", group="Design"),
        InputSpec("string_length", "String Length in Hole", "number",
                  unit="m", group="Design"),
        InputSpec("slurry_volume", "Slurry Volume", "number", unit="bbl",
                  group="Design"),
        InputSpec("ahead_spacer", "Ahead Spacer", "number", unit="bbl",
                  group="Design"),
        InputSpec("behind_spacer", "Behind Spacer", "number", unit="bbl",
                  group="Design"),
        InputSpec("displacement_vol", "Displacement Volume", "number",
                  unit="bbl", group="Design"),
        InputSpec("slurry_density", "Slurry Density", "number", unit="pcf",
                  default="118", group="Slurry"),
        InputSpec("cement_type", "Cement Type", "combo",
                  options=["Class G (Tehran)", "Class G + silica", "Class H",
                           "G + O-Cfr8"], group="Slurry"),
        InputSpec("additives", "Additives", "text",
                  placeholder="e.g. O-Cfr8 0.44 lb/sk, Anti-foam 0.03 gal/sk",
                  group="Slurry"),
        InputSpec("mix_water", "Mix Water", "number", unit="bbl",
                  group="Slurry"),
        InputSpec("slurry_yield", "Slurry Yield", "number", unit="cu ft/sk",
                  default="1.31", group="Slurry"),
        InputSpec("sacks", "Cement Sacks", "number", unit="sks",
                  group="Slurry"),
        InputSpec("woc", "WOC Time", "number", unit="hrs", default="12",
                  group="Job"),
        InputSpec("tag_after", "Tag After (minimum)", "number", unit="hrs",
                  default="12", group="Job"),
        InputSpec("test_pressure", "Plug Test Pressure", "number", unit="psi",
                  default="500", group="Job"),
        InputSpec("cement_unit", "Cement Unit", "text",
                  placeholder="e.g. twin pump, 2 units", group="Job"),
        InputSpec("line_test", "Line Test", "number", unit="psi",
                  default="3000", group="Job"),
    ],
    markdown=r"""
# CEMENT PLUG PROGRAM — Well {{well_name}} — Plug at {{plug_depth}} m

**Field:** {{field}} | **Rig:** {{rig}} | **Job Type:** CMT PLUG
**Revision:** {{revision}} | **Date:** {{doc_date}}

## 1. CEMENTING JOB DESIGN AND CALCULATIONS

| Parameter | Value |
|---|---|
| Client | {{field}} |
| Rig Name | {{rig}} |
| Well | {{well_name}} |
| Job Type | Cement Plug |
| Plug Depth (MD) | {{plug_depth}} m |
| Plug Length | {{plug_length}} m |
| Hole Size | {{hole_size}} in |
| Drill Pipe | {{string}} ({{string_length}} m in hole) |
| Slurry Volume | {{slurry_volume}} bbl |
| Ahead Spacer | {{ahead_spacer}} bbl |
| Behind Spacer | {{behind_spacer}} bbl |
| Displacement until Top of Plug | {{displacement_vol}} bbl |
| Recommended Displacement (Short) | 1.5 bbl |

> **Note:** Total length of cement slurry when string is in hole:
> {{plug_length}} m. Displacement, under-displacement, behind spacer,
> wet stands and top of cement are calculated based on assumed hole size,
> drill pipe size, plug depth and slurry volume — recalculate on the rig
> with final information.

## 2. SLURRY DESIGN

| Material | Conc. | UOM | Qty for Job |
|---|---|---|---|
| Cement G ({{cement_type}}) | 110 | lb/sk | {{sacks}} sks |
| Additives ({{additives}}) | | | |
| Mix Water | | | {{mix_water}} bbl |
| Mix Fluid | | | as per lab |

**Slurry Parameters:**

| Parameter | Value |
|---|---|
| Slurry Volume | {{slurry_volume}} bbl |
| Slurry Density | {{slurry_density}} pcf |
| Slurry Yield | {{slurry_yield}} cu ft/sk |
| Mix Water | {{mix_water}} gal/sk (per lab) |

- Lab result sheet attached; slurry approved before job.
- 100% back-up additives and 30% back-up cement available.

## 3. JOB PROCEDURE

### 3.1 Preparation

1. Rig up cement unit ({{cement_unit}}); pressure test lines to
   {{line_test}} psi.
2. Calibrate density and flow meters; check data acquisition.
3. Mix and test slurry per lab; record density continuously.
4. Pre-job safety meeting with all personnel; PJSM.

### 3.2 Pumping

1. Pump {{ahead_spacer}} bbl ahead spacer at
   {{pump_rate}} bpm.
2. Mix and pump {{slurry_volume}} bbl slurry
   ({{slurry_density}} pcf) at {{slurry_rate}} bpm.
3. Drop top plug (if applicable); displace with {{displacement_vol}} bbl
   at {{displacement_rate}} bpm.
4. **Under-displacement:** leave {{under_displacement}} bbl
   (displace until top of plug at {{plug_top_depth}} m).
5. Pull pipe slowly to {{pull_up_to}} m (above plug top); reverse
   circulate excess slurry.

### 3.3 Post-Job

1. WOC {{woc}} hrs.
2. Tag plug at {{plug_depth}} m ± tolerance; record.
3. Pressure test plug to {{test_pressure}} psi (if required).
4. Continue operations per next program.

## 4. HOLD POINTS

| HP | Stage | Hold Point |
|---|---|---|
| HP-01 | Design | Calculations checked by WSS + cementing operator |
| HP-02 | Job | Plug pumped; displacement complete |
| HP-03 | WOC | Tagged and tested |

## 5. CONTINGENCIES

- **Premature set:** pull above plug, circulate; inform office.
- **Lost circulation while pumping:** reduce rate, continue with program,
  evaluate returns.
- **Plug not tagged at expected depth:** wash down carefully, tag, or
  set additional plug as required.

## 6. HSE

- High-pressure operation — barricade; no personnel near lines.
- Chemical handling per SDS; PPE.
- Night job: sufficient lighting, fuel tanks checked each 2 hrs.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

CEMENT_PLUG_PROC.inputs += [
    InputSpec("pump_rate", "Ahead Spacer Rate", "number", unit="bpm",
              default="5", group="Job"),
    InputSpec("slurry_rate", "Slurry Pump Rate", "number", unit="bpm",
              default="4", group="Job"),
    InputSpec("displacement_rate", "Displacement Rate", "number", unit="bpm",
              default="5", group="Job"),
    InputSpec("under_displacement", "Under-Displacement", "number",
              unit="bbl", group="Job"),
    InputSpec("plug_top_depth", "Top of Plug (after POOH)", "number",
              unit="m", group="Job"),
    InputSpec("pull_up_to", "Pull Pipe Up To", "number", unit="m",
              group="Job"),
]

# ----------------------------------------------------------------------------
# 19. WELL KILL / WELL CONTROL PROCEDURE (FIELD STYLE)
# ----------------------------------------------------------------------------
# Based on real field procedure "WELL SI-009 Killing well procedure No8"
# — history-based kill plan with staged approach.
# ----------------------------------------------------------------------------

NISOC_KILL_PROC = TemplateDef(
    key="nisoc_kill_procedure",
    name="Well Kill Procedure (Field style)",
    icon="🛑",
    kind="Procedure",
    description=(
        "Real field well-kill procedure (SI-009 style): short history, "
        "kill fluid weight decision, staged kill steps, notes on losses, "
        "gains, stripping and BHA change."),
    inputs=_well_inputs() + [
        InputSpec("short_history", "Short History (loss/gain/stuck)", "textarea",
                  required=True,
                  placeholder="e.g. complete loss @3084m, stuck @3060m, "
                  "gain 100 BPH during POOH",
                  group="History"),
        InputSpec("kill_mw", "Kill Mud Weight", "number", unit="pcf",
                  required=True, group="Kill"),
        InputSpec("kill_depth", "Kill Depth (TD)", "number", unit="m",
                  group="Kill"),
        InputSpec("bha_plan", "BHA for Kill Run", "text",
                  placeholder="e.g. 8-3/8\" bit (open nozzles) + BHA w/o stabilizer",
                  group="Kill"),
        InputSpec("gain_control", "Gain Control During POOH", "text",
                  placeholder="e.g. close well periodically, bullhead gained volume",
                  group="Kill"),
        InputSpec("loss_treatment", "Loss Treatment", "text",
                  placeholder="e.g. LCM pill / cement plug", group="Kill"),
        InputSpec("stripping", "Stripping Allowed", "combo",
                  options=["NO — not recommended", "YES"],
                  group="Kill"),
    ],
    markdown=r"""
# WELL KILLING PROCEDURE — No. {{revision}} — {{well_name}}

**Field:** {{field}} | **Rig:** {{rig}} | **Revision:** {{revision}} | **Date:** {{doc_date}}

## SHORT HISTORY

{{short_history}}

## KILL PLAN

**Kill mud weight:** {{kill_mw}} pcf — **Kill depth:** {{kill_depth}} m

### Step 1 — POOH to Surface

1. POOH to surface and lay down current bit & BHA.
2. **Note (gain control):** {{gain_control}}.
3. **Note (stripping):** {{stripping}} — if hydril rubber spare is not
   available, stripping is NOT recommended; use periodic bullheading to
   control well during trip.

### Step 2 — RIH with Kill BHA

1. RIH with {{bha_plan}} to bottom ({{kill_depth}} m).
2. RIH carefully; monitor gains/losses continuously.

### Step 3 — Circulate & Uniform Mud Weight

1. Circulate and uniform mud weight to **{{kill_mw}} pcf**; ensure well
   is static.
2. **In case of loss:** use {{loss_treatment}} to cure loss.
3. Check hole stability at various pump rates ({{hole_check}}).
4. Confirm well dead: shut in, monitor {{shut_in_time}} minutes — no
   pressure build-up.

### Step 4 — POOH and Secure

1. POOH to surface, lay down kill BHA.
2. Secure well; next program to be issued in due time.

## HOLD POINT

> **HP:** Well static at {{kill_mw}} pcf — confirmed by Company
> Supervisor before proceeding.

## CONTINGENCIES

- **Gain while killing:** close well, bullhead gained volume, increase MW
  in stages within hole stability limits.
- **Cannot increase MW (mud condition):** re-assess, use staged kill with
  heavier pills, consult office.
- **Loss + gain simultaneously:** treat losses first with LCM/plug, keep
  hole full, then continue kill.

## HSE

- Well control drills before operation; H2S watch ({{h2s}}).
- No stripping without approved plan and equipment.
- Continuous communication driller – supervisor – office.

## APPROVAL

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared By | {{prepared_by}} | | |
| Approved By | {{approved_by}} | | |
""",
)

NISOC_KILL_PROC.inputs += [
    InputSpec("hole_check", "Hole Stability Check", "text",
              placeholder="e.g. circulate at 300/500/700 gpm — monitor returns",
              group="Kill"),
    InputSpec("shut_in_time", "Shut-in Confirmation", "number", unit="min",
              default="30", group="Kill"),
]

# ----------------------------------------------------------------------------
# REGISTRY
# ----------------------------------------------------------------------------

PROCEDURE_TEMPLATES: List[TemplateDef] = [
    TRIPPING_PROC,
    RUN_CASING_PROC,
    CASING_CEMENT_PROC,
    BOP_TEST_PROC,
    KICK_PROC,
    NISOC_KILL_PROC,
    STUCK_PIPE_PROC,
    SLICKLINE_PROC,
    ESP_RUN_PROC,
    PACKER_SET_PROC,
    PERFORATION_PROC,
    DST_PROC,
    WELLHEAD_PROC,
    LOST_CIRC_PROC,
    CEMENT_PLUG_PROC,
    RIG_MOVE_PROC,
    H2S_PROC,
    TUBING_TEST_PROC,
    BHA_PROC,
]
