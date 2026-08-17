# ============================================================================
# DEFAULT INPUT VALUES — complete coverage of every template input
# File: tests/defaults.py
# Used by tests/validate_outputs.py to feed realistic default data into
# every capability so outputs can be validated for format + content.
# ============================================================================

from typing import Dict, List, Optional

# realistic values for the most important keys
REALISTIC = {
    # identity (neutral)
    "operator": "the Operator", "contractor": "the Service Company",
    "prepared_by": "Engineer", "reviewed_by": "Lead Engineer",
    "approved_by": "Drilling Manager",
    "revision": "01", "doc_date": "17-August-2026",
    "well_name": "Well A", "field": "Field X", "field_name": "Field X",
    "reservoir": "Main Reservoir", "target_formation": "Main Reservoir",
    "target_zone": "Main Zone", "zone": "Main Zone",
    "target": "Main Reservoir", "interval": "Main Reservoir",
    "rig": "Rig 1", "rig_name": "Rig 1", "rig_type": "Land Rig",
    "country": "Country X", "province": "Province Y", "block": "Block X", "pad_name": "Pad 1",
    "coordinate_system": "UTM", "zero_ref": "KB", "wh_latitude": "0",
    "wh_longitude": "0", "wh_x": "0", "wh_y": "0", "loc_n": "0",
    "loc_e": "0",
    # geometry / depth (ft unless noted)
    "depth": "10000", "depth_ft": "10000", "td_depth": "10000",
    "total_depth": "10000", "td_md": "10000", "total_depth_md": "10000",
    "depth_m": "3050", "td_m": "3050", "td_tvd": "9800",
    "vertical_td": "9500", "target_depth": "10000", "landing_depth": "9800",
    "landing_tvd": "9600", "lateral_length": "2000", "lateral_td": "12000",
    "kop": "3000", "kop_depth": "3000", "kb_elevation": "30",
    "rt_elevation": "30", "ground_elevation": "0", "rkb_msl": "30",
    "datum_depth": "0", "datum_pressure": "14.7", "air_gap": "0",
    "water_depth": "0",
    # hole / pipe / casing (in)
    "hole_size": "12.25", "hole_id": "12.25", "hole_diameter": "12.25",
    "bit_size": "12.25", "pipe_od": "5", "pipe_size": "5",
    "drill_pipe_od": "5", "dp_id": "4.276", "pipe_id": "4.276",
    "bha_od": "8", "bha_length": "600", "dc_length": "600",
    "casing_size": "9.625", "casing_od": "9.625", "casing_id": "8.921",
    "casing_wall": "0.472", "casing_wall_in": "0.472",
    "wall_thickness": "0.472", "casing_yield": "110000",
    "casing_yield_psi": "110000", "yield_strength": "110000",
    "casing_depth": "8000", "casing_depth_ft": "8000", "shoe_depth": "8000",
    "csg_depth": "8000", "casing_weight": "47", "casing_weight_ppf": "47",
    "weight_ppf": "47", "liner_size": "7", "tubing_size": "3.5",
    "tubing_string": "3.5 in, L80, 9.3 ppf",
    "shoe_size": "9.625", "shoe_track": "60", "toc": "4000",
    "conductor": "20 in @ 100 ft", "string_size": "5", "string_length": "9000",
    # fluids
    "mud_weight": "12", "mud_weight_ppg": "12", "current_mw": "12",
    "mw": "12", "mud_type": "Oil Based Mud", "mud_type1": "OBM",
    "mud_type2": "WBM", "mud_type3": "Spacer",
    "mw1": "12", "mw2": "14", "mw3": "16",
    "yield_point": "20", "mud_yp": "20", "yp_lb100ft2": "20",
    "plastic_viscosity": "25", "mud_pv": "25", "pv_cp": "25",
    "n_index": "0.6", "flow_index": "0.6", "k_index": "120",
    "consistency_index": "120", "yield_stress": "8", "tau0": "8",
    "hb_yield_stress": "8", "fluid_loss": "50", "fluid_loss_ml30": "50",
    "lcm_type": "Medium Nut Plug", "lcm_concentration": "20",
    "lcm_volume": "100", "spot_pill": "Pipe-loosening pill",
    "spot_volume": "80", "base_fluid": "Diesel", "base_fluid_volume": "200",
    "additives": "Caustic soda, soda ash, PAC LV, barite",
    "mud_chemicals": "Caustic soda 0.5 lb/bbl; PAC LV 1 lb/bbl",
    "solids_control": "Shakers 200 mesh + desilter + centrifuge",
    "fluid_tests": "pH 10.5, FL 3 cc, gel 4/8",
    "mud_props": "MW 12 ppg, PV 25, YP 20, FL 3",
    "mud_range": "11.5-12.5 ppg",
    "vertical_mud": "12 ppg OBM", "working_fluid": "12 ppg OBM",
    "fill_fluid": "12 ppg OBM", "treatment_fluid": "12 ppg OBM",
    "frac_fluid": "Cross-linked gel", "proppant": "20/40 ISP",
    "proppant_schedule": "1-5 ppa staged",
    "well_fluid": "12 ppg OBM", "fluid": "12 ppg OBM",
    "spacer": "Water-based spacer 13 ppg", "spacer_density": "13",
    "spacer_volume": "60", "ahead_spacer": "30", "behind_spacer": "30",
    "displacement": "20", "displacement_rate": "5",
    "displacement_vol": "300", "displacement_volume": "300",
    "flush_rate": "5", "flush_volume": "40", "wash": "10 bbl spacer",
    "wash_volume": "40", "pad_volume": "30",
    # pressures / gradients
    "formation_pressure": "11", "pore_pressure": "11", "pp_ppg": "11",
    "fracture_gradient": "16", "fg_ppg": "16", "frac_gradient": "16",
    "fg": "16", "pressure_gradient": "0.57", "oil_gradient": "0.35",
    "reservoir_pressure": "5000", "reservoir_temperature": "200",
    "pressure_psi": "5000", "expected_whp": "3000",
    "wellhead_pressure": "2000", "tubing_pressure": "1500",
    "annulus_pressure": "1000", "flow_temp": "150",
    "max_pressure": "10000", "test_pressure": "5000",
    "low_pressure": "300", "high_pressure": "5000",
    "max_annulus_pressure": "3000", "max_ct_pressure": "5000",
    "max_squeeze_pressure": "3000", "squeeze_rate": "2",
    "breakdown_pressure": "4500", "inject_pressure": "3000",
    "inject_rate": "2", "isip": "2500", "datum_pressure2": "14.7",
    "maasp": "2000", "masp": "2000",
    # well control
    "sidpp": "400", "sidpip": "200", "sicp": "600",
    "shut_in_casing_pressure": "600", "pit_gain": "20",
    "max_pit_gain": "20", "pit_gain_bbl": "20", "annular_capacity": "0.045",
    "ann_cap_bbl_ft": "0.045", "kick_tolerance": "1.5",
    "bop_wp": "10000", "bop_working_pressure": "10000", "bop_wp_psi": "10000",
    "bop_rating": "10000", "bop_stack": "Ram BOP stack; annular + rams",
    "pipe_rams": "2 x 5 in pipe rams; blind shear",
    "choke": "2 x 4 in chokes", "choke_manifold": "10K 3 x 4 in",
    "chokes": "2 x 4 in", "separator": "Gas buster + flare",
    "returns_manifold": "4 in", "kill_fluid": "12.5 ppg OBM",
    "kill_fluid_weight": "12.5", "kill_mw": "12.5", "kill_method": "Wait and Weight",
    "primary_method": "Wait and Weight", "secondary_method": "Bullheading",
    "kill_plan": "Wait and Weight method",
    "kill_volume": "400", "kill_time": "2", "kill_depth": "8000",
    "kill_hydrostatic": "5200", "kill_surface_pressure": "2000",
    "kill_barriers": "BOP rams; kill fluid", "icp": "1500", "fcp": "800",
    "slow_pump_rates": "0.5 bbl/min @ 400 psi",
    "slow_pump_pressure": "800", "spr_psi": "800",
    "pump_output": "0.1", "pump_output_bbl_stk": "0.1",
    "shut_in_procedure": "1. Stop rotation; 2. pick up; 3. shut BOP; "
                         "4. record pressures",
    "stripping": "Stripping procedure per operator policy",
    "flow_expected": "Yes", "flow_period": "30", "flow_period_2": "30",
    "gas_handling": "Divert to flare", "gain_control": "Trip tank",
    "trip_tank": "Trip tank in service", "trip_gain_alarm": "5",
    "trip_loss_alarm": "5", "h2s": "No", "h2s_level": "0",
    "h2s_alarm": "10", "h2s_drills": "Weekly", "h2s_plan":
    "H2S detection, PPE, drills, wind sock",
    "emergency_contact": "Drilling office", "medical": "Rig medic on board",
    # hydraulics
    "flow_rate": "500", "flow_rate_gpm": "500", "q_gpm": "500",
    "pump_rate": "500", "circ_rate": "500", "circulation_rate": "500",
    "circulation_time": "2", "condition_time": "1", "ann_velocity": "100",
    "tfa": "0.3312", "tfa_in2": "0.3312", "nozzle_area": "0.3312",
    "nozzles": "3 x 12/32", "nozzle_velocity": "350", "jet_impact": "2.5",
    "bit_hsi": "3.5", "hsi": "3.5", "bit_pressure_drop": "800",
    "sys_pressure_loss": "300", "spp": "2800", "ecm": "0.0",
    "ecd": "12.4", "ecd_max": "12.6", "surface_type": "Type 2 (standard)",
    "spm": "90", "chip_velocity": "0.5",
    # drilling parameters
    "wob": "25", "wob_klbf": "25", "rpm": "100", "rotary_speed": "100",
    "rotate_rpm": "100", "rop": "30", "rop_target": "30",
    "torque": "15000", "torque_min": "10000", "torque_max": "20000",
    "torque_limits": "20000 ft-lb max", "torque_log": "Yes",
    "max_overpull": "50", "max_pull": "400", "max_slackoff": "30",
    "overpull": "20", "slack_off": "10", "pull_up_to": "50",
    "trip_speed": "60", "trip_speed_ft_min": "60", "trip_speed_cased": "90",
    "rih_speed": "90", "running_speed": "90", "approach_speed": "5",
    "move_distance": "30", "max_dls": "3", "bur": "3",
    # directional
    "well_type": "Development", "well_profile": "J-Shape",
    "well_classification": "Class I", "well_status": "Active",
    "build_rate": "3", "max_inc": "35", "hold_inclination": "35",
    "hold_azimuth": "90", "max_dls2": "3", "horizontal_displacement": "1500",
    "survey_interval": "100", "survey_tool": "MWD",
    "anti_collision": "Maintain separation factor > 1.5",
    "target_x": "0", "target_y": "0", "inc_tolerance": "1",
    "slide_ratio": "35%", "coordinate_system2": "UTM",
    "directional_plan": "Build to 35 deg at 3 deg/30m, hold to TD",
    "trajectory_table": ("| MD (ft) | Inc (°) | Az (°) |\n|---|---|---|\n"
                         "| 0 | 0 | 90 |\n| 5000 | 35 | 90 |\n"
                         "| 10000 | 35 | 90 |"),
    # BHA / bit
    "bha": "12.25 in PDC + motor + MWD + DC + HWDP + DP",
    "bha_desc": "12.25 in PDC bit; 9.5 in motor; 8 in stabilizer; MWD; "
                "6.5 in DC; HWDP; 5 in DP",
    "bha_plan": "Run assembly per program",
    "bit_type": "PDC", "bit_table": "|Size|Type|Nozzles|\n|---|---|---|\n"
                "|12.25|PDC|3x12/32|",
    "bha_table": "|Item|OD|Length|\n|---|---|---|\n|Bit|12.25|0.5|",
    "drilling_params_table": "|Section|WOB|RPM|Flow|\n|---|---|---|---|\n"
                "|12.25|25|100|500|",
    "assembly": "12.25 in PDC + motor assembly", "jar": "Hydraulic jar",
    "jars": "Hydraulic jar in BHA", "up_jar": "1", "down_jar": "1",
    "jar_hold": "30 min", "jar_timeout": "2", "engage_weight": "20",
    "up_cycles": "5", "down_cycles": "5", "work_cycles": "10",
    "shock_tool": "Shock sub", "stabilizer": "8 in string stabilizer",
    # casing / cement
    "casing_program": "20 in @ 500 ft; 13.375 in @ 4000 ft; 9.625 in "
                      "@ 10000 ft",
    "casing_table": "|Size|Depth|Grade|Weight|\n|---|---|---|---|\n"
                    "|9.625|8000|L80|47|",
    "casing_ratings_table": "|Size|Burst|Collapse|\n|---|---|---|\n"
                "|9.625|8000|6000|",
    "cement_type": "Class G", "slurry_type": "Class G + 35% silica",
    "slurry": "Class G, 15.8 ppg", "slurry_approved": "Approved",
    "slurry_density": "15.8", "slurry_yield": "1.18", "slurry_rate": "5",
    "slurry_volume": "500", "lead_slurry": "Class G + 2% gel",
    "tail_slurry": "Class G + silica", "lead_density": "14.5",
    "tail_density": "16.2", "lead_yield": "1.18", "tail_yield": "1.05",
    "lead_volume": "300", "tail_volume": "200", "lead_rate": "5",
    "tail_rate": "3", "lead_tt": "60", "tail_tt": "45",
    "excess": "30", "excess_pct": "30", "woc": "8", "woc_time": "8",
    "cemented_length": "8000", "cement_interval_ft": "8000",
    "water_per_sack": "5.2", "mix_water": "5.2", "centralizers": "Every 60 ft",
    "float_equipment": "Float shoe + collar", "cement_head": "Quick union",
    "cement_unit": "Twin pump", "cement_units": "2 x twin pump",
    "bulk_cement": "500 sk on site", "sacks": "500", "mix_water_bbl": "50",
    "toc2": "4000", "cement_program": "Lead 14.5 ppg + tail 16.2 ppg",
    "cement_table": "|Stage|Density|Volume|\n|---|---|---|\n|Lead|14.5|300|",
    "cbl_required": "Yes", "cbl": "CBL/VDL after 24 h WOC",
    "spacer2": "60 bbl", "displacement_fluid": "12 ppg OBM",
    "plug_top_depth": "3000", "plug1_depth": "3000", "plug2_depth": "6000",
    "plug1_volume": "100", "plug1_test": "2000", "plug_bump": "1500",
    "plug_hold": "30", "plug_test": "2000", "plug_volume": "100",
    "plug_depth": "3000", "plug_set": "Set on tags", "plug_type": "Cement",
    "plug_length": "150", "plugs_table": "|Plug|Depth|Test|\n|---|---|---|\n"
                "|P1|3000|2000|",
    "test_plug": "Test plug", "toc_depth": "4000", "top_cement": "4000",
    # completion / wellhead
    "wellhead_type": "Compact wellhead", "wellhead_pressures": "5K x 10K",
    "wellhead_test_pressure": "5000", "packer": "Retrievable packer",
    "packer_depth": "9500", "packer_setting_pressure": "4000",
    "packer_test": "3000", "packer_shallow_test": "2000",
    "p_seal_test": "5000", "trsv_depth": "500", "trsv_hold_pressure": "4000",
    "trsv_test": "Function tested", "twcv_test": "5000",
    "ssd_depth": "9500", "ssd_test": "3000", "ring_gaskets": "BX-156",
    "ring_gasket_size": "13.625", "stud_torque": "300 ft-lb",
    "tubing_test": "5000", "string_test": "5000",
    "string_test_pressure": "5000", "surface_test_pressure": "3000",
    "body_test": "10000", "drain_valve_test": "5000",
    "check_valve_test": "3000", "agv_run_pressure": "2000",
    "agv_test": "2000", "surface_plug_depth": "500",
    "perforation_interval": "9800-9820 ft",
    "producing_interval": "9800-9820 ft", "completion_type": "Single",
    "completion_plan": "Single completion with TRSV + SSD",
    "completion_before": "Well cleaned, packer fluid in hole",
    "completion_after": "Well handed over to production",
    "completion_description": "Single 3.5 in completion",
    "completion_summary": "TRSV at 500 ft, packer at 9500 ft",
    "completion_date": "01-Dec-2026",
    "packer2": "Retrievable", "isolation": "Packer + TRSV",
    "gas_lift": "No", "esp_supplier": "—",
    # fishing / stuck pipe
    "fish_description": "Parted 5 in drill pipe fish in hole",
    "fish_condition": "Fish top in good condition",
    "fish_od": "5", "fish_id": "4.276", "fish_top": "8500",
    "fish_length": "1500", "fish_neck": "Fish neck 4.5 in",
    "fish_decision": "Recover fish", "free_point": "8500",
    "previous_attempts": "No previous attempts", "jarring_plan": "Jar up to 50 klbf",
    "can_rotate": "No", "can_circulate": "Yes", "can_move_pipe": "No",
    "stuck_interval": "8500-8700 ft",
    # workover / intervention
    "workover_type": "Workover", "job_type": "Workover",
    "operation": "Workover", "operation_type": "Workover",
    "job_objective": "Replace failed completion",
    "objective": "Replace completion and restore production",
    "well_objective": "Drill and complete the well",
    "well_history": "Previously completed as single producer",
    "short_history": "Offset wells drilled without major problems",
    "drilling_history": "No major issues in offset wells",
    "requirements": "Rig, BOP, completion equipment, services",
    "equipment_table": "|Item|Status|\n|---|---|\n|BOP|Tested|",
    "services_table": "|Service|Provider|\n|---|---|\n|Mud|—|",
    "cost_table": "|Item|Cost|\n|---|---|\n|Rig|1000000|",
    "time_table": "|Phase|Days|\n|---|---|\n|Drill|30|",
    "evaluation_table": "|Item|Value|\n|---|---|\n|Reservoir|Main|",
    "formations_table": "|Top|Depth|\n|---|---|\n|Main|5000|",
    "hazards_table": "|Hazard|Mitigation|\n|---|---|\n|H2S|Monitor|",
    # time & cost
    "total_days": "45", "time_days": "45", "duration": "45",
    "duration_days": "45", "days": "45", "report_days": "45",
    "prelim_days": "5", "npt_contingency": "10", "npt_percent": "10",
    "total_cost": "12000000", "estimated_cost": "12000000",
    "afe_total": "12000000", "cost_per_m": "3800",
    "phase1_time": "5", "phase2_time": "10", "phase3_time": "15",
    "phase4_time": "10", "phase5_time": "5", "phase6_time": "0",
    # drilling problems & response
    "problem": "Intermittent losses observed in offset wells",
    "rate_loss": "10 bbl/hr", "recovered_volume": "200 bbl",
    "expected_rate": "5 bbl/min", "expected_fill": "30",
    "loss_treatment": "LCM pills, reduce MW if safe",
    "lcm_pill": "Medium nut plug 20 ppb",
    # HPHT / geomechanics / special
    "max_temperature": "350", "max_temp_f": "350",
    "reservoir_temperature_f": "350", "temperature_change": "150",
    "delta_t": "150", "dT_f": "150", "co2": "3", "co2_pct": "3",
    "sigma_v_grad": "1.9", "overburden_gradient": "1.9",
    "sH_sv_ratio": "0.63", "sigmaH_sv_ratio": "0.63",
    "sh_sv_ratio": "0.53", "sigmah_sv_ratio": "0.53",
    "ucs_psi": "8000", "rock_ucs": "8000", "friction_angle": "30",
    "friction_angle_deg": "30", "tensile_strength": "500",
    "tensile_strength_psi": "500", "lot_pressure": "1400", "lot_psi": "1400",
    "lot_type": "LOT", "fit": "LOT",
    "burst_load": "9000", "design_burst": "9000", "collapse_load": "6000",
    "design_collapse": "6000", "axial_load": "400000",
    "design_axial": "400000", "df_burst": "1.1", "df_collapse": "1.1",
    "df_tension": "1.6", "leak_tolerance": "5",
    "packer_set": "Yes", "tree_ok": "Yes", "trsv_ok": "Yes",
    "cement_verified": "Yes", "casing_tested": "Yes", "tubing_tested": "Yes",
    "wellhead_ok": "Yes", "bop_ok": "Yes",
    # rig & misc
    "mooring": "8 point", "riser": "21 in riser", "riser_tensioners": "8 x 80 kips",
    "viv": "VIV strakes fitted", "dp_capability": "DP class 2",
    "winterization": "Yes", "simo": "None", "heater": "Mud heater",
    "burner": "Test separator burner", "blender": "Mud blender",
    "intensifier": "CT intensifier pump", "injector": "CT injector head",
    "ct_unit": "CT unit", "ct_size": "1.75 in", "ct_length": "20000",
    "ct_operation": "Milling", "ct_bop": "CT BOP stack",
    "ct_inspection": "Visual + wall thickness",
    "pump": "Triplex pump", "pump_model": "T-1600", "pump_unit": "1 x triplex",
    "gauge": "Dead weight tester", "gauges": "Dead weight tester",
    "gauge_program": "Calibrated before job", "gauge_run": "Yes",
    "samplers": "Mud sampler", "sampling": "Every 10 m",
    "samples": "Cuttings + fluid samples", "gas_samples": "Gas trap samples",
    "oil_samples": "Oil samples at shows", "water_samples": "Water samples",
    "dst": "DST #1 planned", "dst_tools": "DST tools on site",
    "tester_valve": "Tester valve", "correlation": "Synthetic seismogram",
    "correlation_ref": "Well A", "coring": "Core 1 planned",
    "sample_tools": "Core barrel", "tbc": "TBC on site",
    "anchor": "Anchor tested", "oil_gradient2": "0.35",
    "water_cut": "0%", "api_gravity": "32",
    "well_conditions": "Normal pressure, no H2S",
    "well_control_plan": "Kill sheet updated daily",
    "well_integrity": "Barriers verified",
    "well_architecture": "Conductor + surface + production casing",
    "hydrate_plan": "Inhibited fluids, no long shutdowns",
    "hydrate_remediation": "MEG injection",
    "shallow_gas_plan": "Divert to flare, avoid shallow hole",
    "shallow_hazards": "None expected",
    "disconnect_criteria": "DP offset limits",
    "disconnect_matrix": "DP watch circle",
    "disconnect_test": "Tested weekly",
    "offset_wells": "Offset wells: none",
    "offset_limits": "SF > 1.5",
    "critical_depths": "8500 ft",
    "confirmation": "Confirmed", "verification": "Verified",
    "hole_check": "Hole in good condition", "tag_check": "Tagged at TD",
    "tag_after": "0", "fill_interval": "500", "fill_volume": "20",
    "expected_fill2": "0", "flow_alarm": "2 bbl", "level_tolerance": "1",
    "monitor_interval": "5", "monitor_time": "2", "attempt_limit": "3",
    "max_surface_pressure_psi": "3000",
}


def default_for_key(key: str, spec=None) -> str:
    """Return a realistic default for any input key."""
    if key in REALISTIC:
        return REALISTIC[key]
    if spec is not None:
        t = getattr(spec, "type", "text")
        if t == "combo" and getattr(spec, "options", None):
            for o in spec.options:
                if o and o.lower() not in ("none", "select", "n/a"):
                    return o
            return spec.options[0] if spec.options else ""
        if t == "check":
            return "YES"
        if t == "table":
            cols = getattr(spec, "columns", None) or ["Item"]
            return " | ".join("Value" for _ in cols)
        if t == "textarea":
            return "Default text for this field — filled by the validation harness."
        if t == "number":
            low = key.lower()
            if any(x in low for x in ("mw", "mud_weight", "density",
                                      "ppg", "pcf", "sg")):
                return "12"
            if "temp" in low or "temperature" in low:
                return "200"
            if "depth" in low or "td_" in low or "tvd" in low or "md_" in low:
                return "10000"
            if "pressure" in low or "psi" in low or "test" in low:
                return "5000"
            if "days" in low or "duration" in low or "time" in low or \
                    "hours" in low or "period" in low:
                return "10"
            if "cost" in low or "budget" in low or "amount" in low:
                return "1000000"
            if "rate" in low or "flow" in low or "gpm" in low:
                return "500"
            if "speed" in low or "velocity" in low or "ft_min" in low:
                return "60"
            if "rpm" in low:
                return "100"
            if "wob" in low:
                return "25"
            if "size" in low or "od" in low or "id" in low or "diameter" \
                    in low or "hole" in low or "bit" in low:
                return "9.625"
            if "pct" in low or "percent" in low or "excess" in low:
                return "10"
            if "weight" in low or "load" in low or "pull" in low or \
                    "klb" in low or "force" in low:
                return "50"
            return "100"
        # text
        return "Specified"
    return "Specified"


def build_default_values(templates) -> Dict:
    """Complete default dataset covering every template input plus the
    realistic core (placeholders like reviewed_by that templates use but
    do not declare as inputs are covered by the REALISTIC map)."""
    vals = dict(REALISTIC)
    for td in templates:
        for s in td.inputs:
            if s.key not in vals:
                vals[s.key] = default_for_key(s.key, s)
    return vals


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from wizard_library import ALL_TEMPLATES
    from wizard_procedures import PROCEDURE_TEMPLATES
    from wizard_offshore import OFFSHORE_TEMPLATES
    from wizard_master import build_master_templates
    tpl = (list(ALL_TEMPLATES) + list(PROCEDURE_TEMPLATES) +
           list(OFFSHORE_TEMPLATES) + build_master_templates())
    vals = build_default_values(tpl)
    keys = {s.key for td in tpl for s in td.inputs}
    print("templates:", len(tpl), "| unique input keys:", len(keys),
          "| defaults built:", len(vals))
    missing = keys - set(vals)
    print("missing:", len(missing), list(missing)[:10])
