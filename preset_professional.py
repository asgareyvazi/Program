# ============================================================================
# PROFESSIONAL PRESET - REALISTIC DRILLING PROJECT
# File: preset_professional.py
# Based on: Shell DEP, Saudi Aramco SAES, BP GP Standards
# 
# HOW TO USE:
#   1. Place this file in the same folder as the other 5 files
#   2. Run:  python preset_professional.py
#   3. Output Word document will be generated and opened automatically
# ============================================================================

import sys
import os
from pathlib import Path
from datetime import datetime

def check_and_install():
    """بررسی و نصب وابستگی‌ها"""
    required = {'docx': 'python-docx'}
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            print(f"📦 Installing {package}...")
            import subprocess
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, "--quiet"
            ])
            print(f"   ✅ {package} installed")

check_and_install()

# ============================================================================
# IMPORT DATA MODELS
# ============================================================================

from main import (
    WellProject, CompanyInfo, WellGeneralInfo,
    FormationTop, HazardEntry, CasingDesign,
    CementDesign, BHADesign, MudProgram,
    DirectionalPlan, BOPStack, WellControlData,
    RigSpecification, DrillingParameters, TimeEstimate,
    DrillStringComponent, EvaluationProgram, HydraulicsData
)


def create_professional_project() -> WellProject:
    """
    ایجاد پروژه حرفه‌ای کامل
    بر اساس یک چاه واقعی توسعه‌ای جهتی در خاورمیانه
    شامل تمام جزئیات مهندسی
    """
    
    project = WellProject()

    # ================================================================
    # 1. COMPANY & DOCUMENT INFORMATION
    # ================================================================
    project.company_info = CompanyInfo(
        operator_name="ARABIAN GULF PETROLEUM COMPANY (AGPC)",
        operator_logo_path="",
        contractor_name="NATIONAL OILWELL DRILLING COMPANY (NODC)",
        contractor_logo_path="",
        field_name="AL-SHAHEEN FIELD",
        well_name="ASH-0247-H1",
        well_number="0247",
        pad_name="PAD-18 (Cluster E)",
        rig_name="NODC RIG-112 (2000 HP AC/VFD)",
        rig_type="Land Rig",
        country="UNITED ARAB EMIRATES",
        region="Abu Dhabi - Onshore Concession Block 4",
        block_license="ADNOC Concession Agreement - Block 4 Extension",
        api_number="UAE-ADNOC-ASH-2024-0247",
        spud_date="2024-09-15",
        prepared_by="Eng. Ahmad K. Al-Rashidi\n"
                     "Senior Drilling Engineer\n"
                     "MSc Petroleum Engineering - Imperial College London\n"
                     "IWCF Level 4 Certified",
        reviewed_by="Eng. Mohammed S. Al-Fahad\n"
                     "Drilling Superintendent\n"
                     "BSc Petroleum Engineering\n"
                     "25 Years Experience",
        approved_by="Eng. Khalid A. Al-Mansouri\n"
                     "Drilling Manager - AGPC\n"
                     "MBA, BSc Petroleum Engineering\n"
                     "30 Years Experience",
        revision="A",
        document_number="AGPC-DRL-ASH0247-PRG-2024-001",
        classification="CONFIDENTIAL - RESTRICTED DISTRIBUTION"
    )

    # ================================================================
    # 2. WELL GENERAL INFORMATION
    # ================================================================
    project.well_info = WellGeneralInfo(
        well_type="Development",
        well_profile="Directional J-Type",
        total_depth_md=14850,
        total_depth_tvd=11200,
        water_depth=0,
        air_gap=0,
        ground_elevation=142.5,
        kb_elevation=32.8,
        rt_elevation=32.8,
        magnetic_declination=2.18,
        grid_convergence=0.92,
        surface_latitude="24° 28' 15.34\" N",
        surface_longitude="54° 22' 48.72\" E",
        target_latitude="24° 29' 02.15\" N",
        target_longitude="54° 23' 18.45\" E",
        coordinate_system="WGS 84 / UTM Zone 40N",
        seismic_reference="3D Seismic Survey 2022 (Al-Shaheen Phase-III)\n"
                          "Reference Lines: ASH-IL-2245 to ASH-IL-2260\n"
                          "XL-1180 to XL-1220\n"
                          "Interpreted by: GeoTech Solutions - Report GTS-2023-0456\n"
                          "Structural mapping confidence: High (95%)\n"
                          "Depth conversion uncertainty: ±25 ft at reservoir level",
        wellhead_type="Cameron 13-5/8\" x 10M Compact Wellhead",
        xmas_tree_type="Cameron Conventional Tree - 10K WP",
        target_formation="Arab-D Reservoir (Upper Unit - Zone 2B)",
        target_zone="Arab-D Zone 2B - Dolomitized Grainstone",
        expected_reservoir_pressure=5120,
        expected_reservoir_temperature=252,
        expected_h2s_concentration=4.2,
        expected_co2_concentration=2.8,
        nace_required=True
    )

    # ================================================================
    # 3. FORMATION TOPS (PROGNOSIS)
    # ================================================================
    project.formation_tops = [
        FormationTop(
            name="Recent / Quaternary",
            formation_type="Sand",
            md_top=0, md_bottom=180,
            tvd_top=0, tvd_bottom=180,
            pore_pressure_top=8.55, pore_pressure_bottom=8.55,
            fracture_gradient_top=13.0, fracture_gradient_bottom=13.5,
            overburden_gradient=15.5,
            temperature_top=90, temperature_bottom=100,
            drillability="Very Easy",
            directional_tendency="Neutral",
            remarks="Unconsolidated sand/gravel. Possible shallow water flow. "
                    "Maintain controlled ROP < 60 ft/hr."
        ),
        FormationTop(
            name="Dibdibba Formation",
            formation_type="Sandstone",
            md_top=180, md_bottom=680,
            tvd_top=180, tvd_bottom=680,
            pore_pressure_top=8.55, pore_pressure_bottom=8.60,
            fracture_gradient_top=13.5, fracture_gradient_bottom=14.2,
            overburden_gradient=15.8,
            temperature_top=100, temperature_bottom=118,
            drillability="Easy",
            directional_tendency="Neutral",
            remarks="Semi-consolidated sandstone with minor clay. "
                    "Freshwater aquifer protection zone. "
                    "Surface casing seat candidate at 680 ft."
        ),
        FormationTop(
            name="Fars / Lower Fars",
            formation_type="Marl",
            md_top=680, md_bottom=1450,
            tvd_top=680, tvd_bottom=1450,
            pore_pressure_top=8.60, pore_pressure_bottom=8.65,
            fracture_gradient_top=14.2, fracture_gradient_bottom=14.8,
            overburden_gradient=16.2,
            temperature_top=118, temperature_bottom=140,
            drillability="Easy",
            directional_tendency="Neutral",
            remarks="Marl and clay with thin limestone stringers. "
                    "Good seal formation."
        ),
        FormationTop(
            name="Dammam Formation",
            formation_type="Limestone",
            md_top=1450, md_bottom=2850,
            tvd_top=1450, tvd_bottom=2850,
            pore_pressure_top=8.65, pore_pressure_bottom=8.75,
            fracture_gradient_top=14.8, fracture_gradient_bottom=15.2,
            overburden_gradient=16.5,
            temperature_top=140, temperature_bottom=168,
            drillability="Medium",
            directional_tendency="Neutral",
            remarks="Crystalline to chalky limestone. "
                    "⚠ CAUTION: Lost circulation possible in fractured/vugular zones. "
                    "Have LCM ready. "
                    "Offset well ASH-0198 experienced 15 bbl/hr losses at 2100-2300 ft."
        ),
        FormationTop(
            name="Rus Formation",
            formation_type="Anhydrite",
            md_top=2850, md_bottom=3650,
            tvd_top=2850, tvd_bottom=3650,
            pore_pressure_top=8.75, pore_pressure_bottom=8.85,
            fracture_gradient_top=15.2, fracture_gradient_bottom=15.6,
            overburden_gradient=17.0,
            temperature_top=168, temperature_bottom=182,
            drillability="Medium",
            directional_tendency="Neutral",
            remarks="Anhydrite interbedded with marl and thin dolomite. "
                    "Bit balling possible in marl sections. "
                    "Good shoe location for intermediate casing at base."
        ),
        FormationTop(
            name="Umm Er Radhuma (UER)",
            formation_type="Limestone",
            md_top=3650, md_bottom=5800,
            tvd_top=3650, tvd_bottom=5500,
            pore_pressure_top=8.85, pore_pressure_bottom=9.20,
            fracture_gradient_top=15.6, fracture_gradient_bottom=16.0,
            overburden_gradient=17.5,
            temperature_top=182, temperature_bottom=208,
            drillability="Medium",
            directional_tendency="Build",
            remarks="Dolomitic limestone. KOP planned at 4200 ft in upper UER. "
                    "⚠ SEVERE LOST CIRCULATION ZONE at 4800-5200 ft "
                    "(vugs and fractures). "
                    "Offset ASH-0212: Total losses, required 200 bbl cement plug. "
                    "Pre-treat mud with fine/medium LCM before entering zone."
        ),
        FormationTop(
            name="Simsima Formation",
            formation_type="Limestone",
            md_top=5800, md_bottom=7200,
            tvd_top=5500, tvd_bottom=6600,
            pore_pressure_top=9.20, pore_pressure_bottom=9.50,
            fracture_gradient_top=16.0, fracture_gradient_bottom=16.5,
            overburden_gradient=18.0,
            temperature_top=208, temperature_bottom=225,
            drillability="Hard",
            directional_tendency="Hold",
            remarks="Dense crystalline limestone. Hard drilling expected - "
                    "ROP 8-15 ft/hr. "
                    "Watch for bit wear. PDC with 6-blade recommended."
        ),
        FormationTop(
            name="Aruma Formation (Globotruncana Lst)",
            formation_type="Limestone",
            md_top=7200, md_bottom=8500,
            tvd_top=6600, tvd_bottom=7500,
            pore_pressure_top=9.50, pore_pressure_bottom=9.80,
            fracture_gradient_top=16.5, fracture_gradient_bottom=16.8,
            overburden_gradient=18.5,
            temperature_top=225, temperature_bottom=235,
            drillability="Hard",
            directional_tendency="Hold",
            remarks="Argillaceous limestone with chert nodules. "
                    "Chert can cause PDC bit damage - monitor bit wear. "
                    "Consider hybrid bit if multiple runs needed."
        ),
        FormationTop(
            name="Wasia Formation (Mauddud / Nahr Umr)",
            formation_type="Sandstone",
            md_top=8500, md_bottom=10200,
            tvd_top=7500, tvd_bottom=8600,
            pore_pressure_top=9.80, pore_pressure_bottom=10.20,
            fracture_gradient_top=16.8, fracture_gradient_bottom=17.0,
            overburden_gradient=18.8,
            temperature_top=235, temperature_bottom=242,
            drillability="Medium",
            directional_tendency="Drop",
            remarks="Interbedded sandstone, shale, and limestone (Mauddud Mbr). "
                    "Nahr Umr Shale at base - reactive shale section. "
                    "Potential for differential sticking in Mauddud sands. "
                    "Intermediate casing shoe target: base of Wasia (~10200 ft MD)."
        ),
        FormationTop(
            name="Shuaiba Formation",
            formation_type="Limestone",
            md_top=10200, md_bottom=11400,
            tvd_top=8600, tvd_bottom=9400,
            pore_pressure_top=10.20, pore_pressure_bottom=10.50,
            fracture_gradient_top=17.0, fracture_gradient_bottom=17.2,
            overburden_gradient=19.0,
            temperature_top=242, temperature_bottom=245,
            drillability="Hard",
            directional_tendency="Hold",
            remarks="Dense, low porosity limestone. "
                    "Slow drilling - ROP 5-10 ft/hr. "
                    "Minor mud losses possible."
        ),
        FormationTop(
            name="Kharaib Formation (Hawar / Lekhwair)",
            formation_type="Limestone",
            md_top=11400, md_bottom=12800,
            tvd_top=9400, tvd_bottom=10200,
            pore_pressure_top=10.50, pore_pressure_bottom=10.80,
            fracture_gradient_top=17.0, fracture_gradient_bottom=17.2,
            overburden_gradient=19.2,
            temperature_top=245, temperature_bottom=248,
            drillability="Hard",
            directional_tendency="Hold",
            remarks="Dense limestone with dolomite. Hawar Shale marker at top. "
                    "Transition zone to reservoir. "
                    "Increase H₂S monitoring - trace H₂S may appear."
        ),
        FormationTop(
            name="Arab-D Reservoir",
            formation_type="Dolomite",
            md_top=12800, md_bottom=14850,
            tvd_top=10200, tvd_bottom=11200,
            pore_pressure_top=10.80, pore_pressure_bottom=10.95,
            fracture_gradient_top=17.0, fracture_gradient_bottom=17.5,
            overburden_gradient=19.5,
            temperature_top=248, temperature_bottom=255,
            drillability="Medium-Hard",
            directional_tendency="Hold",
            remarks="🎯 PRIMARY TARGET - Arab-D Upper Unit (Zone 2B).\n"
                    "Dolomitized grainstone/packstone with good porosity (15-22%). "
                    "Reservoir pressure: 5120 psi. BHT: 255°F.\n"
                    "⚠ H₂S CONCENTRATION: 4.2% - ALL NACE MR-0175 MATERIALS REQUIRED.\n"
                    "⚠ CO₂: 2.8% - Corrosion-resistant materials.\n"
                    "Use OBM to minimize formation damage. "
                    "ROP control for optimal hole cleaning. "
                    "Minimize overbalance to prevent differential sticking.\n"
                    "Offset ASH-0231: IP = 4,500 BOPD from Arab-D Zone 2B."
        ),
    ]

    # ================================================================
    # 4. ANTICIPATED HAZARDS
    # ================================================================
    project.hazards = [
        HazardEntry(
            hazard_type="Shallow Water Flow",
            md_top=0, md_bottom=400,
            severity="Medium", probability="Possible",
            description="Shallow aquifer in Recent/Dibdibba sands. "
                        "Potential for water flow during conductor drilling.",
            mitigation="Diverter system installed and function tested. "
                       "Controlled ROP < 60 ft/hr in top 400 ft. "
                       "Monitor returns for water influx.",
            contingency="Activate diverter system. "
                        "Set conductor immediately if flow encountered. "
                        "Prepare weighted mud to kill flow.",
            reference_well="ASH-0145 (water flow at 280 ft, controlled with diverter)"
        ),
        HazardEntry(
            hazard_type="Lost Circulation",
            md_top=1450, md_bottom=2850,
            severity="Medium", probability="Likely",
            description="Fractured and vugular zones in Dammam Fm. "
                        "Offset well ASH-0198 experienced 15 bbl/hr losses at 2100-2300 ft.",
            mitigation="Pre-treat active mud with 5 ppb fine calcium carbonate. "
                       "Have 100 bbl LCM pill ready. "
                       "Monitor ECD continuously. "
                       "Control ROP to minimize surge/swab.",
            contingency="Spot LCM pill (Nut Plug + Mica blend). "
                        "If >30 bbl/hr, stop drilling and spot settable pill. "
                        "Cement squeeze if total losses.",
            reference_well="ASH-0198 (15 bbl/hr losses, treated with LCM pills)"
        ),
        HazardEntry(
            hazard_type="Lost Circulation",
            md_top=4800, md_bottom=5200,
            severity="High", probability="Almost Certain",
            description="SEVERE loss zone in UER - vugular porosity, natural fractures. "
                        "3 of 5 offset wells experienced total losses in this interval.",
            mitigation="Pre-treat mud with 15 ppb LCM blend before entering zone. "
                       "Reduce flow rate by 20% through loss zone. "
                       "Have 300 bbl cement ready for plug. "
                       "Prepare settable pill system.",
            contingency="Immediate LCM pill (100 bbl concentrated). "
                        "If total losses: cement plug (100-200 ft balanced plug). "
                        "WOC 12 hrs, drill out and re-test. "
                        "Consider setting intermediate casing above zone if repeated losses.",
            reference_well="ASH-0212 (total losses at 5050 ft, 200 bbl cement plug, "
                          "successful after 2 attempts)"
        ),
        HazardEntry(
            hazard_type="Stuck Pipe",
            md_top=8500, md_bottom=10200,
            severity="High", probability="Possible",
            description="Differential sticking risk in permeable Mauddud sands. "
                        "High overbalance (>1000 psi) in this section.",
            mitigation="Minimize static time in open hole (<5 min per connection). "
                       "Keep pipe moving (rotate/reciprocate) at all times. "
                       "Maintain jar in BHA. "
                       "Use lubricant in mud system (3-5% by volume). "
                       "Monitor differential pressure - keep overbalance minimum.",
            contingency="Immediate: work pipe, apply jar. Do NOT pull >50 klbs overpull. "
                        "Spot diesel/mineral oil pill (100 bbl) across stuck zone. "
                        "Soak 4-8 hrs, reattempt. "
                        "If unsuccessful: free point survey, backoff, fish or sidetrack.",
            reference_well="ASH-0189 (stuck at 9420 ft, freed with oil pill after 6 hrs)"
        ),
        HazardEntry(
            hazard_type="Sloughing Shale",
            md_top=9600, md_bottom=10200,
            severity="Medium", probability="Likely",
            description="Nahr Umr Shale - highly reactive, swelling clays. "
                        "Potential for tight hole, pack-off, and wellbore enlargement.",
            mitigation="Use inhibitive mud system (KCl-Polymer or OBM). "
                       "Maintain minimum 4% KCl concentration. "
                       "Maintain mud weight within window. "
                       "Pump hi-vis sweeps every 500 ft. "
                       "Wiper trips every 1000 ft.",
            contingency="If pack-off: increase mud weight 0.2-0.3 ppg. "
                        "Increase KCl to 7%. "
                        "Consider converting to OBM if problems persist. "
                        "Short trip to shoe every 500 ft.",
            reference_well="ASH-0223 (tight hole, required wiper trip every 500 ft)"
        ),
        HazardEntry(
            hazard_type="H2S Gas",
            md_top=12800, md_bottom=14850,
            severity="Critical", probability="Almost Certain",
            description="H₂S concentration 4.2% (42,000 ppm) in Arab-D Reservoir. "
                        "IMMEDIATELY DANGEROUS TO LIFE AND HEALTH (IDLH). "
                        "CO₂ at 2.8% contributing to corrosion.",
            mitigation="ALL tubulars and equipment NACE MR-0175/ISO 15156 compliant. "
                       "H₂S detection system: fixed monitors at critical locations + "
                       "portable monitors for all personnel. "
                       "SCBA units at all muster points and on rig floor. "
                       "Wind socks at 4 corners of rig. "
                       "H₂S safety briefing for ALL personnel. "
                       "Zinc carbonate scavenger in mud system (5 ppb). "
                       "Buddy system enforced. "
                       "H₂S drills conducted before entering zone.",
            contingency="ALERT (10 ppm): Notify all, check wind direction, SCBA ready. "
                        "ALARM (20 ppm): Sound alarm, non-essential evacuate, SCBA on. "
                        "EMERGENCY (50+ ppm): Full evacuation to upwind muster. "
                        "RESCUE: ONLY with SCBA. Do NOT enter without protection. "
                        "Medical: O₂ administration, CPR if needed. "
                        "Hospital: Al-Ain International Hospital - 45 min by road.",
            reference_well="ASH-0231 (H₂S measured at 4.1% during DST, no incidents)"
        ),
        HazardEntry(
            hazard_type="High Temperature",
            md_top=10200, md_bottom=14850,
            severity="Medium", probability="Almost Certain",
            description="BHT up to 255°F (124°C) at TD. "
                        "Impact on: MWD/LWD tools, mud properties, cement design.",
            mitigation="Use HT-rated MWD/LWD tools (rated to 300°F). "
                       "HT mud system with thermal stability additives. "
                       "HT cement design with retarder adjusted for BHCT. "
                       "Monitor mud properties at regular intervals. "
                       "Lime/calcium management for OBM stability.",
            contingency="If tool failure: POOH, redress tools, add heat shield. "
                        "If mud degradation: adjust chemistry, add stabilizer. "
                        "Maintain spare HT tools on location.",
            reference_well="Multiple offset wells - standard for this field"
        ),
        HazardEntry(
            hazard_type="Kick / Well Control",
            md_top=12800, md_bottom=14850,
            severity="Critical", probability="Possible",
            description="Reservoir pressure 5120 psi (10.95 ppg EMW). "
                        "Narrow margin between pore pressure and fracture gradient. "
                        "H₂S makes any kick extremely hazardous.",
            mitigation="Maintain mud weight 0.3-0.5 ppg above pore pressure. "
                       "Monitor pit volume continuously (±0.5 bbl sensitivity). "
                       "Flow check every connection. "
                       "Slow pump rates recorded every tour and after any change. "
                       "Well control drills weekly. "
                       "Kill sheet posted and updated.",
            contingency="Hard shut-in procedure (API RP 59). "
                        "Wait & Weight method (preferred for H₂S). "
                        "Kill mud available at all times. "
                        "Maximum kick tolerance: 50 bbl gas at shoe.",
            reference_well="ASH-0178 (2 bbl gas kick at 13200 ft, killed successfully "
                          "with W&W method in 4 hrs)"
        ),
        HazardEntry(
            hazard_type="Anti-Collision Risk",
            md_top=4200, md_bottom=14850,
            severity="Medium", probability="Unlikely",
            description="Adjacent wells on PAD-18: ASH-0231, ASH-0235, ASH-0238. "
                        "Minimum planned separation: 150 ft at closest approach.",
            mitigation="Anti-collision survey plan with definitive surveys at all key depths. "
                       "Use gyro surveys at casing shoes for accuracy. "
                       "Real-time anti-collision monitoring (Compass software). "
                       "Separation factor > 1.5 at all points. "
                       "Closest approach at 8500 ft MD (150 ft from ASH-0235).",
            contingency="If separation factor < 1.5: stop drilling, take definitive survey. "
                        "If SF < 1.0: emergency trajectory correction. "
                        "Coordinate with offset well operations.",
            reference_well="Standard practice for PAD-18 cluster"
        ),
    ]

    # ================================================================
    # 5. CASING DESIGN
    # ================================================================
    project.casing_design = [
        CasingDesign(
            section_name="Conductor",
            section_type="Conductor",
            hole_size=36,
            casing_od=30, casing_id=28.000,
            casing_weight=309.72, casing_grade="X-56",
            casing_connection="Welded (AWS D1.1)",
            setting_depth_md=300, setting_depth_tvd=300,
            shoe_depth_md=300, shoe_depth_tvd=300,
            top_of_cement_md=0, cement_to_surface=True,
            burst_rating=2800, collapse_rating=1100,
            tensile_rating=550000, drift_id=28.000,
            min_design_factor_burst=1.10,
            min_design_factor_collapse=1.10,
            min_design_factor_tension=1.60,
            centralizer_type="Rigid Centralizer",
            centralizer_spacing=40,
            float_collar_depth=260,
            float_shoe_type="Guide Shoe - Texas Pattern",
            number_of_joints=8,
            scratchers=False, is_liner=False,
            casing_accessories="Guide Shoe, Float Collar, 8 Rigid Centralizers",
            remarks="Drive or drill & cement. Protect shallow aquifer. "
                    "Verify conductor alignment with survey."
        ),
        CasingDesign(
            section_name="Surface",
            section_type="Surface",
            hole_size=26,
            casing_od=20, casing_id=18.730,
            casing_weight=133.00, casing_grade="K-55",
            casing_connection="Buttress Thread & Coupled (BTC)",
            setting_depth_md=2900, setting_depth_tvd=2900,
            shoe_depth_md=2900, shoe_depth_tvd=2900,
            top_of_cement_md=0, cement_to_surface=True,
            burst_rating=3060, collapse_rating=1490,
            tensile_rating=1161000, drift_id=18.630,
            min_design_factor_burst=1.10,
            min_design_factor_collapse=1.10,
            min_design_factor_tension=1.80,
            centralizer_type="Bow-Spring (Weatherford Zip-Set)",
            centralizer_spacing=60,
            float_collar_depth=2840,
            float_shoe_type="Float Shoe w/ Circulation Ports",
            number_of_joints=72,
            scratchers=True, is_liner=False,
            casing_accessories="Float Shoe, Float Collar, Landing Collar, "
                               "48 Bow-Spring Centralizers, "
                               "24 Stop Collars, "
                               "12 Cement Baskets (every 250 ft), "
                               "Stage Collar at 1500 ft (backup)",
            remarks="Cement to surface - regulatory requirement. "
                    "Protect freshwater aquifers. "
                    "Set in Dammam Fm limestone for competent shoe. "
                    "Verify cement returns at surface. "
                    "If no returns, top up through back-side."
        ),
        CasingDesign(
            section_name="Intermediate",
            section_type="Intermediate",
            hole_size=17.5,
            casing_od=13.375, casing_id=12.415,
            casing_weight=72.00, casing_grade="N-80 (Type 1)",
            casing_connection="Buttress Thread & Coupled (BTC)",
            setting_depth_md=10200, setting_depth_tvd=8600,
            shoe_depth_md=10200, shoe_depth_tvd=8600,
            top_of_cement_md=6000,
            burst_rating=5020, collapse_rating=2670,
            tensile_rating=1556000, drift_id=12.259,
            min_design_factor_burst=1.10,
            min_design_factor_collapse=1.10,
            min_design_factor_tension=1.80,
            centralizer_type="Bow-Spring (Weatherford Zip-Set II)",
            centralizer_spacing=50,
            float_collar_depth=10140,
            float_shoe_type="Float Shoe w/ PDC Drillable Insert",
            number_of_joints=254,
            scratchers=True, is_liner=False,
            casing_accessories="Float Shoe (PDC Drillable), Float Collar, "
                               "Landing Collar, "
                               "204 Bow-Spring Centralizers, "
                               "100 Stop Collars, "
                               "24 Rigid Centralizers (across open hole deviated section), "
                               "Spiral Centralizers in 3000-4000 ft interval, "
                               "DV Tool at 8000 ft (differential valve - optional)",
            remarks="Critical casing string - isolates loss zones and build section. "
                    "Cement across UER loss zone for isolation. "
                    "Verify cement integrity with CBL/VDL. "
                    "Consider rotating casing during cement job. "
                    "Shoe set in Nahr Umr Shale (competent formation)."
        ),
        CasingDesign(
            section_name="Production",
            section_type="Production",
            hole_size=12.25,
            casing_od=9.625, casing_id=8.535,
            casing_weight=53.50, casing_grade="L-80 (13Cr Modified)",
            casing_connection="VAM TOP HC (Premium Gas-Tight)",
            setting_depth_md=14850, setting_depth_tvd=11200,
            shoe_depth_md=14850, shoe_depth_tvd=11200,
            top_of_cement_md=8500,
            burst_rating=8750, collapse_rating=5300,
            tensile_rating=1310000, drift_id=8.379,
            min_design_factor_burst=1.15,
            min_design_factor_collapse=1.125,
            min_design_factor_tension=1.80,
            centralizer_type="Bow-Spring (Weatherford Turbulizer)",
            centralizer_spacing=35,
            float_collar_depth=14780,
            float_shoe_type="Auto-Fill Float Shoe (PDC Drillable)",
            number_of_joints=370,
            scratchers=True, is_liner=False,
            casing_accessories="Auto-Fill Float Shoe (PDC drillable), "
                               "Auto-Fill Float Collar, "
                               "Landing Collar with debris trap, "
                               "420 Bow-Spring Centralizers (Turbulizers), "
                               "185 Stop Collars, "
                               "48 Rigid Centralizers (deviated section >30°), "
                               "10 External Casing Packers (across Arab-D), "
                               "Scratchers/Wipers every joint across reservoir",
            remarks="⚠ SOUR SERVICE CASING - ALL NACE MR-0175 / ISO 15156 COMPLIANT. "
                    "L-80 13Cr for H₂S and CO₂ resistance. "
                    "VAM TOP HC premium connections - gas-tight to 100% of body rating. "
                    "Cement integrity critical for reservoir isolation. "
                    "CBL/CBIL required across full reservoir interval. "
                    "All casing handling per API RP 5C1 - no damage to threads. "
                    "Running speed < 2 ft/s to control surge. "
                    "Reciprocate and rotate during cementing."
        ),
    ]

    # ================================================================
    # 6. CEMENT DESIGN
    # ================================================================
    project.cement_design = [
        CementDesign(
            section_name="Surface",
            casing_od=20, hole_size=26,
            shoe_depth_md=2900, toc_md=0,
            lead_slurry_type="API Class G + 35% Silica Flour + Perlite Extender",
            lead_slurry_density=12.8,
            lead_slurry_yield=1.52,
            lead_slurry_volume=480,
            lead_slurry_thickening_time=10,
            lead_slurry_compressive_strength=450,
            tail_slurry_type="API Class G + 35% Silica Flour (Neat)",
            tail_slurry_density=15.8,
            tail_slurry_yield=1.15,
            tail_slurry_volume=150,
            tail_slurry_thickening_time=6,
            tail_slurry_compressive_strength=2500,
            spacer_type="Weighted Chemical Spacer (MudPush II)",
            spacer_density=10.0,
            spacer_volume=40,
            wash_type="Fresh Water + Surfactant",
            wash_volume=25,
            displacement_fluid="Original Mud",
            displacement_volume=520,
            displacement_rate=8,
            max_ecd=14.8,
            excess_percentage=100,
            woc_time=12,
            plug_bump_pressure=500,
            cement_additives="Retarder (HR-25): 0.3% BWOC, "
                             "Fluid Loss Additive (Halad-344): 0.5% BWOC, "
                             "Dispersant (CFR-3): 0.3% BWOC, "
                             "Defoamer: 0.02 gal/sk, "
                             "Silica Flour: 35% BWOC, "
                             "Perlite (lead only): 15% BWOC",
            stage_cementing=False,
            squeeze_required=False,
            cbl_cbil_required=True,
            remarks="Cement to surface. "
                    "Circulate 2x bottoms up before cementing. "
                    "Reciprocate casing ±15 ft during cement placement. "
                    "Verify returns at surface. "
                    "If no returns, top up through 2\" backside line. "
                    "Min 10 min contact time across formation. "
                    "Lab test: BHCT = 155°F, BHST = 170°F."
        ),
        CementDesign(
            section_name="Intermediate",
            casing_od=13.375, hole_size=17.5,
            shoe_depth_md=10200, toc_md=6000,
            lead_slurry_type="API Class G + 35% Silica Flour + "
                             "20% Microspheres (3M HGS)",
            lead_slurry_density=12.2,
            lead_slurry_yield=2.05,
            lead_slurry_volume=620,
            lead_slurry_thickening_time=12,
            lead_slurry_compressive_strength=280,
            tail_slurry_type="API Class G + 35% Silica Flour + "
                             "Anti-Gas Migration Additive",
            tail_slurry_density=16.0,
            tail_slurry_yield=1.12,
            tail_slurry_volume=200,
            tail_slurry_thickening_time=8,
            tail_slurry_compressive_strength=2800,
            spacer_type="Engineered Spacer (MudPush II + Viscosifier)",
            spacer_density=11.5,
            spacer_volume=50,
            wash_type="Chemical Wash Package (Base + Acid Wash)",
            wash_volume=30,
            displacement_fluid="Original Mud",
            displacement_volume=650,
            displacement_rate=6,
            max_ecd=16.2,
            excess_percentage=50,
            woc_time=18,
            plug_bump_pressure=800,
            cement_additives="Retarder (HR-25): 0.5% BWOC, "
                             "Fluid Loss (Halad-413): 0.8% BWOC, "
                             "Dispersant (CFR-3): 0.4% BWOC, "
                             "Anti-Gas Migration (GasStop HT): 2.0% BWOC, "
                             "Silica Flour: 35% BWOC, "
                             "Microspheres (lead): 20% BWOC, "
                             "Defoamer: 0.02 gal/sk, "
                             "Friction Reducer: 0.15 gal/sk",
            stage_cementing=False,
            squeeze_required=False,
            cbl_cbil_required=True,
            remarks="Critical cement job - must isolate UER loss zones. "
                    "ECD management critical - do not exceed frac gradient. "
                    "Rotate casing at 10-15 RPM during cement placement. "
                    "Reciprocate if rotation not possible. "
                    "Anti-gas migration additive in tail to prevent gas channeling. "
                    "CBL/VDL/CBIL logging required across 6000-10200 ft. "
                    "Min CBL amplitude < 5 mV for acceptable bond. "
                    "Lab test: BHCT = 218°F, BHST = 240°F."
        ),
        CementDesign(
            section_name="Production",
            casing_od=9.625, hole_size=12.25,
            shoe_depth_md=14850, toc_md=8500,
            lead_slurry_type="API Class G + 35% Silica Flour + "
                             "20% Microspheres + H₂S Resistant",
            lead_slurry_density=11.8,
            lead_slurry_yield=2.15,
            lead_slurry_volume=520,
            lead_slurry_thickening_time=14,
            lead_slurry_compressive_strength=220,
            tail_slurry_type="API Class G + 40% Silica Flour + "
                             "Anti-Gas Migration + H�ite Latex",
            tail_slurry_density=16.5,
            tail_slurry_yield=1.06,
            tail_slurry_volume=180,
            tail_slurry_thickening_time=10,
            tail_slurry_compressive_strength=3500,
            spacer_type="Oil-Based Spacer (compatible with OBM)",
            spacer_density=11.5,
            spacer_volume=40,
            wash_type="Base Oil Wash + Mutual Solvent + Chemical Wash",
            wash_volume=35,
            displacement_fluid="OBM (original mud)",
            displacement_volume=580,
            displacement_rate=4.5,
            max_ecd=17.2,
            excess_percentage=50,
            woc_time=24,
            plug_bump_pressure=1200,
            cement_additives="Retarder (HR-25L): 0.8% BWOC, "
                             "Fluid Loss (Halad-600): 1.0% BWOC, "
                             "Dispersant (CFR-5L): 0.5% BWOC, "
                             "Anti-Gas Migration (GasStop HT): 3.0% BWOC, "
                             "Latex (CemFlex): 1.5 gal/sk, "
                             "Silica Flour: 35-40% BWOC, "
                             "H₂S Scavenger (IronSponge): 5% BWOC, "
                             "Microspheres (lead): 20% BWOC, "
                             "Expanding Agent (MicroBond): 0.5% BWOC, "
                             "Defoamer: 0.03 gal/sk",
            stage_cementing=False,
            squeeze_required=False,
            cbl_cbil_required=True,
            remarks="⚠ CRITICAL CEMENT JOB - SOUR SERVICE.\n"
                    "ALL cement additives H₂S compatible.\n"
                    "Latex additive for micro-annulus prevention.\n"
                    "Expanding agent for long-term bond.\n"
                    "ECD management CRITICAL - max 17.2 ppg EMW.\n"
                    "Rotate casing at 10-15 RPM + reciprocate ±10 ft.\n"
                    "Wiper plugs: OBM-compatible (rubber, not brass).\n"
                    "Oil-based spacer ahead for OBM displacement.\n"
                    "Minimum contact time: 10 min across reservoir.\n"
                    "CBL/CBIL from 8500 ft to TD - 100% coverage.\n"
                    "Acceptance criteria: CBL < 3 mV, CBIL > 80% bonded.\n"
                    "If bond inadequate: remedial squeeze required.\n"
                    "Lab test: BHCT = 235°F, BHST = 255°F."
        ),
    ]

    # ================================================================
    # 7. BHA DESIGNS
    # ================================================================
    project.bha_designs = [
        BHADesign(
            section_name="Surface", bha_number=1,
            hole_size=26, bha_type="Rotary Assembly",
            bit_type="Tricone Insert", bit_size=26,
            bit_manufacturer="Baker Hughes",
            bit_model="Hughes Christensen XR+ 517",
            bit_nozzles="3x24 (TFA = 1.33 sq.in)",
            bit_tfa=1.33,
            motor_type="", motor_od=0, motor_bend=0,
            rss_type="", rss_model="",
            mwd_type="Gyro MWD (Surface Section Only)",
            lwd_type="", lwd_sensors="GR (natural gamma only)",
            stabilizer_sizes='26" Near-bit, 26" String',
            recommended_wob="15-35 klbs",
            recommended_rpm="80-120 RPM (Surface)",
            recommended_flow_rate="900-1100 GPM",
            recommended_torque="25,000 ft-lbs maximum",
            max_wob=35,
            remarks="Rotary assembly for vertical surface hole. "
                    "26\" near-bit stabilizer for hole gauge. "
                    "26\" string stabilizer at 60 ft. "
                    "Pack BHA for stiffness. "
                    "Run gyro survey at shoe for accurate position."
        ),
        BHADesign(
            section_name="Intermediate", bha_number=1,
            hole_size=17.5, bha_type="Motor + MWD/LWD (Build Section)",
            bit_type="PDC", bit_size=17.5,
            bit_manufacturer="NOV (ReedHycalog)",
            bit_model="TKC76 - 6 Blade, 16mm Cutters",
            bit_nozzles="5x16, 2x14 (TFA = 0.98 sq.in)",
            bit_tfa=0.98,
            motor_type="Schlumberger PowerPak 9-5/8\" Positive Displacement Motor",
            motor_od=9.625, motor_bend=1.50,
            motor_lobe="7/8 Lobe",
            motor_flow_range="400-800 GPM",
            rss_type="", rss_model="",
            mwd_type="Schlumberger PowerPulse MWD",
            lwd_type="Schlumberger EcoScope",
            lwd_sensors="GR, Resistivity (Phase/Attenuation), "
                        "Neutron Porosity, Density, PEF, "
                        "Annular Pressure (PWD), Caliper",
            stabilizer_sizes='17-1/2" adjustable near-bit, '
                             '17-3/8" string stabilizer',
            recommended_wob="15-40 klbs (slide: 15-25, rotate: 25-40)",
            recommended_rpm="Slide: 0 RPM (motor only 80-120 RPM). "
                            "Rotate: 100-160 RPM surface + motor",
            recommended_flow_rate="700-850 GPM "
                                  "(motor differential: 400-600 psi)",
            recommended_torque="35,000 ft-lbs maximum",
            max_wob=40,
            remarks="Build section BHA: KOP at 4200 ft, build 3.0°/100ft. "
                    "1.5° motor bend for build rate. "
                    "Slide/Rotate ratio: target 40/60 for 3°/100ft. "
                    "PWD critical for ECD management in loss zones. "
                    "Pull motor every 200 operating hours or at bit change. "
                    "Monitor motor differential pressure for stall indicators."
        ),
        BHADesign(
            section_name="Intermediate", bha_number=2,
            hole_size=17.5, bha_type="Rotary Assembly (Hold Section)",
            bit_type="PDC", bit_size=17.5,
            bit_manufacturer="Baker Hughes",
            bit_model="Dynamus HCM - 5 Blade, 19mm Cutters",
            bit_nozzles="4x16, 3x14 (TFA = 1.10 sq.in)",
            bit_tfa=1.10,
            motor_type="", motor_od=0, motor_bend=0,
            rss_type="", rss_model="",
            mwd_type="Schlumberger PowerPulse MWD",
            lwd_type="Schlumberger EcoScope",
            lwd_sensors="GR, RES, NEU, DEN, PEF, PWD",
            stabilizer_sizes='17-1/2" near-bit (fixed), '
                             '17-3/8" string stab at 30ft, '
                             '17-1/4" string stab at 60ft',
            recommended_wob="25-45 klbs",
            recommended_rpm="120-180 RPM",
            recommended_flow_rate="750-900 GPM",
            recommended_torque="38,000 ft-lbs maximum",
            max_wob=45,
            remarks="Packed rotary assembly for hold section. "
                    "Triple stabilizer for tangent drilling. "
                    "Maintain inclination ±0.5° of plan. "
                    "Run this BHA from end of build to section TD."
        ),
        BHADesign(
            section_name="Production", bha_number=1,
            hole_size=12.25, bha_type="RSS + MWD/LWD (Full Suite)",
            bit_type="PDC", bit_size=12.25,
            bit_manufacturer="Schlumberger (Smith Bits)",
            bit_model="SDi616 SHARC - 6 Blade, 13mm Cutters",
            bit_nozzles="4x13, 2x12 (TFA = 0.68 sq.in)",
            bit_tfa=0.68,
            motor_type="", motor_od=0, motor_bend=0,
            rss_type="Schlumberger PowerDrive X6",
            rss_model="PowerDrive X6 - Push-the-bit RSS",
            mwd_type="Schlumberger TeleScope ICE (HT Version)",
            lwd_type="Schlumberger PeriScope + EcoScope + SonicScope",
            lwd_sensors="GR, Deep Azimuthal Resistivity (PeriScope 15), "
                        "Neutron Porosity, Bulk Density, PEF, "
                        "Sonic (Compressional + Shear), "
                        "Annular Pressure (PWD), "
                        "Caliper (Ultrasonic), "
                        "Drilling Dynamics (MSE, Vibration, Stick-Slip)",
            stabilizer_sizes='12-1/8" integrated in RSS, '
                             '12-1/8" string stab at 90ft',
            recommended_wob="8-25 klbs",
            recommended_rpm="120-200 RPM (optimize with MSE)",
            recommended_flow_rate="550-700 GPM "
                                  "(min 600 GPM for RSS activation)",
            recommended_torque="28,000 ft-lbs maximum",
            max_wob=25,
            remarks="⚠ H₂S ZONE - ALL BHA COMPONENTS NACE COMPLIANT.\n"
                    "RSS for smooth wellbore in reservoir section.\n"
                    "PeriScope 15 for geo-steering (stay in Zone 2B).\n"
                    "SonicScope for real-time mechanical properties.\n"
                    "Drilling dynamics module for vibration mitigation.\n"
                    "MSE optimization for maximum ROP.\n"
                    "Min flow rate 600 GPM for RSS hydraulic activation.\n"
                    "PWD for real-time ECD monitoring in narrow MW window.\n"
                    "All tools rated to 300°F for BHT safety margin.\n"
                    "Plan 2 bit runs: Run 1 to 13500 ft, Run 2 to TD."
        ),
    ]

    # ================================================================
    # 8. MUD PROGRAMS
    # ================================================================
    project.mud_programs = [
        MudProgram(
            section_name="Surface", hole_size=26,
            depth_from=300, depth_to=2900,
            mud_type="WBM - KCl/Polymer (Inhibitive WBM)",
            mud_weight_in=9.0, mud_weight_out=9.5,
            funnel_viscosity=50, plastic_viscosity=18,
            yield_point=16, gel_strength_10s=6,
            gel_strength_10m=12, gel_strength_30m=18,
            fluid_loss=5.0, hthp_fluid_loss=12.0,
            ph=10.0, chlorides=25000, calcium=200,
            mbt=12, sand_content=0.25,
            total_volume_required=1800, active_volume=900,
            reserve_volume=900,
            key_additives="Spud with Gel/Water (~200 bbl), then build:\n"
                          "• KCl: 5-7% by volume (inhibition)\n"
                          "• PHPA (Polyhall-1): 1.5-2.0 ppb (encapsulation)\n"
                          "• PAC-R: 2.0-3.0 ppb (viscosity)\n"
                          "• PAC-L: 1.0-1.5 ppb (fluid loss)\n"
                          "• Starch (Biolose): 3.0-4.0 ppb (fluid loss)\n"
                          "• Soda Ash: 0.5 ppb (hardness removal)\n"
                          "• Caustic Soda: 0.5 ppb (pH control)\n"
                          "• Barite: as needed for MW\n"
                          "• XC Polymer: 0.5 ppb (low-end rheology)\n"
                          "• Biocide: 0.3 ppb",
            solids_control_equipment="4x Derrick FLC-2000 Shakers (API 200 mesh), "
                                     "Centrifugal Degasser, "
                                     "12\" Desander Cones (2x), "
                                     "4\" Desilter Cones (8x), "
                                     "Mud Cleaner",
            ecd_at_shoe=9.8, ecd_at_td=9.9,
            remarks="Start with gel/water spud mud for conductor section. "
                    "Convert to KCl/Polymer at 300 ft for 26\" hole. "
                    "Maintain KCl > 5% for shale inhibition. "
                    "Monitor Dammam losses closely. "
                    "Pre-treat with Fine CaCO₃ (5 ppb) before entering Dammam."
        ),
        MudProgram(
            section_name="Intermediate", hole_size=17.5,
            depth_from=2900, depth_to=10200,
            mud_type="WBM - KCl/Polymer/Glycol (High Performance WBM)",
            mud_weight_in=9.5, mud_weight_out=12.5,
            funnel_viscosity=55, plastic_viscosity=24,
            yield_point=20, gel_strength_10s=8,
            gel_strength_10m=16, gel_strength_30m=22,
            fluid_loss=3.5, hthp_fluid_loss=8.0,
            ph=10.5, chlorides=45000, calcium=300,
            mbt=18, sand_content=0.15,
            total_volume_required=3200, active_volume=1600,
            reserve_volume=1600,
            key_additives="• KCl: 7-10% by volume (enhanced inhibition)\n"
                          "• PHPA: 2.0-3.0 ppb\n"
                          "• Glycol (ShaleGuard): 3-5% by volume (thermal stability)\n"
                          "• PAC-R: 2.5-3.5 ppb\n"
                          "• PAC-L: 1.5-2.0 ppb\n"
                          "• Modified Starch: 4.0-5.0 ppb\n"
                          "• Barite: as needed (up to 12.5 ppg)\n"
                          "• Lubricant (Lube-167): 3-5% by volume\n"
                          "• Fine CaCO₃ (5-10 ppb): LCM prevention\n"
                          "• Medium CaCO₃ (5 ppb): LCM prevention\n"
                          "• XC Polymer: 0.5-1.0 ppb (hole cleaning sweeps)\n"
                          "• Gilsonite: 5 ppb (seepage loss zones)\n"
                          "• Nut Plug Fine: 5 ppb (standby for losses)",
            solids_control_equipment="4x Derrick FLC-2000 Shakers (API 200-230 mesh), "
                                     "Centrifugal Degasser, "
                                     "Mud Cleaner (screens over desilter), "
                                     "2x Decanting Centrifuge (parallel for barite recovery), "
                                     "12\" Desander, 4\" Desilter",
            ecd_at_shoe=12.8, ecd_at_td=13.0,
            remarks="Glycol added for thermal stability above 200°F. "
                    "Increase MW gradually through pore pressure ramp. "
                    "⚠ CRITICAL: ECD management through UER loss zone (4800-5200 ft). "
                    "Reduce flow rate by 20% through loss zone. "
                    "Pre-treat with LCM blend before entering UER. "
                    "Pump hi-vis sweeps (100+ sec/qt) every 500 ft in build section. "
                    "Wiper trips at 5000, 7000, 8500, 9500 ft. "
                    "Nahr Umr Shale (9600-10200): increase PHPA and glycol. "
                    "Condition mud for casing: YP < 15, Gel 10s < 8."
        ),
        MudProgram(
            section_name="Production", hole_size=12.25,
            depth_from=10200, depth_to=14850,
            mud_type="OBM - Mineral Oil Based Mud (Versadril System)",
            mud_weight_in=11.0, mud_weight_out=13.2,
            funnel_viscosity=55, plastic_viscosity=22,
            yield_point=14, gel_strength_10s=7,
            gel_strength_10m=12, gel_strength_30m=16,
            fluid_loss=0, hthp_fluid_loss=3.5,
            ph=0, chlorides=0, calcium=0,
            mbt=0, sand_content=0.08,
            oil_water_ratio="75/25",
            electrical_stability=900,
            total_volume_required=3500, active_volume=1800,
            reserve_volume=1700,
            key_additives="BASE FLUID:\n"
                          "• Mineral Oil (Sarapar 147): Base (75%)\n"
                          "• CaCl₂ Brine (25% w/w): Internal phase (25%)\n\n"
                          "ADDITIVES:\n"
                          "• Primary Emulsifier (VersaMul): 8-12 ppb\n"
                          "• Secondary Emulsifier (VersaCoat): 4-6 ppb\n"
                          "• Organophilic Clay (VG-69): 4-6 ppb\n"
                          "• Lime: 5-8 ppb (alkalinity reserve)\n"
                          "• Fluid Loss (VersaFLC): 4-6 ppb\n"
                          "• Barite (API Grade): as needed for MW\n"
                          "• Rheology Modifier (VersaMod): 0.5-1.5 ppb\n"
                          "• Wetting Agent (VersaWet): 2-4 ppb\n"
                          "• H₂S Scavenger (ZnO): 10-15 ppb\n"
                          "• CaCO₃ Fine (10-30μ): 20-30 ppb (bridging agent)\n"
                          "• CaCO₃ Medium (50-100μ): 10-15 ppb\n"
                          "• HT Stabilizer (VersaHT): 2-3 ppb",
            solids_control_equipment="4x Derrick FLC-2000 Shakers (API 200 mesh), "
                                     "Centrifugal Degasser (for gas-cut mud), "
                                     "2x Decanting Centrifuge (barite recovery), "
                                     "Closed mud system (environmental protection), "
                                     "OBM-rated transfer pumps and mixers",
            ecd_at_shoe=13.5, ecd_at_td=13.8,
            remarks="⚠ OBM SYSTEM FOR RESERVOIR SECTION.\n"
                    "CRITICAL REQUIREMENTS:\n"
                    "1. OBM to minimize formation damage in Arab-D reservoir.\n"
                    "2. CaCO₃ bridging for pore throat sizing (10-100μ range).\n"
                    "3. ZnO at 10-15 ppb for H₂S scavenging.\n"
                    "4. Electrical stability > 800V at all times.\n"
                    "5. OWR maintained at 75/25 (±2%).\n"
                    "6. HTHP FL < 4.0 ml at 255°F.\n"
                    "7. CaCl₂ activity: 0.80-0.85 (matched to formation).\n"
                    "8. VG-69 content for rheology stability at BHT.\n"
                    "9. Lime excess > 3 ppb for alkalinity buffer.\n"
                    "10. Monitor ES, OWR, CaCl₂ every circulation.\n\n"
                    "ENVIRONMENTAL: Closed system, no discharge. "
                    "Cuttings processed through thermal desorption unit.\n\n"
                    "TRANSITION: Convert from WBM to OBM at 10200 ft shoe. "
                    "Displace WBM with spacer train (base oil wash + "
                    "mutual solvent + surfactant) before OBM."
        ),
    ]

    # ================================================================
    # 9. DIRECTIONAL PLAN
    # ================================================================
    project.directional_plan = DirectionalPlan(
        section_name="All Sections",
        survey_tool="MWD Magnetic (Schlumberger PowerPulse) + "
                     "Gyro Survey at all casing shoes + "
                     "In-Run Gyro (IFR GYRODATA) for anti-collision",
        survey_frequency=90,
        kickoff_point_md=4200,
        kickoff_point_tvd=4200,
        build_rate=3.00,
        turn_rate=0.50,
        hold_inclination=38.0,
        hold_azimuth=42.5,
        target_inclination=38.0,
        target_azimuth=42.5,
        max_dls=5.50,
        horizontal_displacement=5850,
        vertical_section=5850,
        closure_distance=5850,
        closure_direction=42.5,
        anti_collision_wells="ASH-0231 (PAD-18, 180 ft separation at 8500 ft MD)\n"
                             "ASH-0235 (PAD-18, 220 ft separation at 12000 ft MD)\n"
                             "ASH-0238 (PAD-18, 310 ft separation at 14000 ft MD)",
        wellpath_data=[
            {'md': 0, 'tvd': 0, 'inclination': 0, 'azimuth': 0,
             'dls': 0, 'ns': '0', 'ew': '0', 'vs': '0',
             'closure_dist': '0', 'closure_dir': '0',
             'build_turn': '', 'remarks': 'Surface'},
            {'md': 2900, 'tvd': 2900, 'inclination': 0, 'azimuth': 0,
             'dls': 0, 'ns': '0', 'ew': '0', 'vs': '0',
             'closure_dist': '0', 'closure_dir': '0',
             'build_turn': '', 'remarks': '20\" Shoe'},
            {'md': 4200, 'tvd': 4200, 'inclination': 0, 'azimuth': 42.5,
             'dls': 0, 'ns': '0', 'ew': '0', 'vs': '0',
             'closure_dist': '0', 'closure_dir': '42.5',
             'build_turn': 'KOP', 'remarks': 'KICKOFF POINT'},
            {'md': 5467, 'tvd': 5100, 'inclination': 38.0, 'azimuth': 42.5,
             'dls': 3.0, 'ns': '312', 'ew': '285', 'vs': '420',
             'closure_dist': '420', 'closure_dir': '42.5',
             'build_turn': 'End Build', 'remarks': 'END OF BUILD'},
            {'md': 7200, 'tvd': 6460, 'inclination': 38.0, 'azimuth': 42.5,
             'dls': 0, 'ns': '860', 'ew': '785', 'vs': '1160',
             'closure_dist': '1160', 'closure_dir': '42.5',
             'build_turn': 'Tangent', 'remarks': ''},
            {'md': 10200, 'tvd': 8600, 'inclination': 38.0, 'azimuth': 42.5,
             'dls': 0, 'ns': '1720', 'ew': '1570', 'vs': '2320',
             'closure_dist': '2320', 'closure_dir': '42.5',
             'build_turn': 'Tangent', 'remarks': '13-3/8\" Shoe'},
            {'md': 12800, 'tvd': 10200, 'inclination': 38.0, 'azimuth': 42.5,
             'dls': 0, 'ns': '2580', 'ew': '2355', 'vs': '3480',
             'closure_dist': '3480', 'closure_dir': '42.5',
             'build_turn': 'Tangent', 'remarks': 'Top Arab-D'},
            {'md': 14850, 'tvd': 11200, 'inclination': 38.0, 'azimuth': 42.5,
             'dls': 0, 'ns': '3250', 'ew': '2965', 'vs': '4390',
             'closure_dist': '4390', 'closure_dir': '42.5',
             'build_turn': 'Tangent', 'remarks': 'TD - 9-5/8\" Shoe'},
        ],
        remarks="Wellpath designed by: Wellbore Consultants Ltd.\n"
                "Survey program: MWD every 90 ft + Gyro at shoes.\n"
                "Anti-collision: Compass Well Planning v5.2.\n"
                "Min separation factor: 1.5 at all survey stations.\n"
                "Definitive gyro surveys at: 2900, 4200 (KOP), "
                "5467 (EOB), 10200 (13-3/8\" shoe), 14850 (TD).\n"
                "Error model: ISCWSA MWD Rev.5 + IFR Gyro."
    )

    # ================================================================
    # 10. BOP & WELL CONTROL
    # ================================================================
    project.bop_stack = BOPStack(
        bop_type="Quad Ram (Cameron Type U-II)",
        working_pressure=10000,
        bore_size=18.75,
        manufacturer="Cameron (SLB)",
        model="Type U-II Quad Ram Stack",
        serial_number="CAM-U2-2019-1456",
        annular_preventer_size=18.75,
        annular_preventer_wp=10000,
        pipe_ram_size='5" (upper), 3-1/2" (lower)',
        blind_ram=True,
        shear_ram=True,
        variable_bore_ram=True,
        casing_shear_ram=False,
        kill_line_size=3.0,
        choke_line_size=3.0,
        choke_manifold_wp=10000,
        kill_manifold_wp=10000,
        diverter_size=30,
        diverter_line_size=12,
        accumulator_capacity=2400,
        accumulator_precharge=1000,
        function_test_frequency="Weekly (or after crew change)",
        pressure_test_frequency="Per Section + After any BOP work",
        bop_test_pressure_low=250,
        bop_test_pressure_high=7000,
        last_test_date="Prior to spud",
        remarks="Stack from bottom to top:\n"
                "1. Casing Spool (13-5/8\" x 10K)\n"
                "2. Pipe Rams - 5\" (lower)\n"
                "3. Pipe Rams - 3-1/2\" (for tripping)\n"
                "4. Blind/Shear Rams (15K shear rating)\n"
                "5. Variable Bore Rams (3-1/2\" to 7\")\n"
                "6. Cameron DL Annular (18-3/4\" x 10K)\n\n"
                "Accumulator: Koomey 72-bottle, 3000 psi WP.\n"
                "Remote panels: Driller's panel + 2 remote panels.\n"
                "Closing time: < 30 sec (rams), < 60 sec (annular).\n"
                "Choke manifold: 2 manual + 1 hydraulic choke.\n"
                "All H₂S service (NACE trim after intermediate shoe)."
    )

    project.well_control = WellControlData(
        maasp_surface=2850,
        maasp_at_shoe=0,
        kick_tolerance=45,
        kill_method="Wait & Weight (Engineer's Method) - "
                     "PREFERRED for H₂S wells",
        slow_pump_rate_1=30,
        slow_pump_pressure_1=920,
        slow_pump_rate_2=20,
        slow_pump_pressure_2=650,
        slow_pump_rate_3=40,
        slow_pump_pressure_3=1180,
        pit_gain_action_level=5,
        gas_detection_action_level=50,
        h2s_action_levels="ALERT: 10 ppm - Notify all, SCBA ready\n"
                          "ALARM: 20 ppm - Sound alarm, evacuate non-essential, SCBA on\n"
                          "DANGER: 50 ppm - Full evacuation to upwind muster\n"
                          "EMERGENCY: 100+ ppm - IDLH, full emergency response\n"
                          "Continuous monitoring with Dräger fixed detectors + "
                          "personal H₂S monitors for all personnel",
        emergency_contacts="COMPANY MAN: Eng. Ahmad Al-Rashidi +971-50-XXX-XXXX\n"
                           "TOOLPUSHER: Mr. James Wilson +971-50-XXX-XXXX\n"
                           "AGPC BASE OFFICE: +971-2-XXX-XXXX (24/7 Emergency)\n"
                           "AGPC HSE DEPARTMENT: +971-2-XXX-XXXX\n"
                           "AL-AIN HOSPITAL: +971-3-XXX-XXXX (40 min by road)\n"
                           "MEDEVAC HELICOPTER: +971-2-XXX-XXXX (National Ambulance)\n"
                           "FIRE DEPARTMENT: 997\n"
                           "POLICE: 999\n"
                           "AMBULANCE: 998\n"
                           "CIVIL DEFENSE: 996\n"
                           "ADNOC EMERGENCY: +971-2-XXX-XXXX",
        nearest_hospital="Al-Ain International Hospital (40 min by road)\n"
                         "MEDEVAC: 25 min by helicopter to Al-Ain Hospital",
        evacuation_route="Primary: Road to Al-Ain (Route E30) - 45 km\n"
                         "Secondary: Desert Track to Highway E22 - 30 km\n"
                         "Helicopter LZ: 100m north of rig - GPS: 24°28'20\"N 54°22'50\"E",
        remarks="Well Control Training: All crew IWCF Level 2 minimum.\n"
                "Driller and Toolpusher: IWCF Level 3/4.\n"
                "Kill sheets updated every tour change.\n"
                "Slow pump rates recorded every tour and after any change.\n"
                "Well control drills: weekly minimum.\n"
                "Kick detection: Pit Volume Totalizer (Martin Decker), "
                "Flow Show, Gas Trap, Mud Logging Gas Chromatograph."
    )

    # ================================================================
    # 11. RIG SPECIFICATIONS
    # ================================================================
    project.rig_spec = RigSpecification(
        rig_name="NODC RIG-112",
        rig_type="Land Rig",
        rig_contractor="National Oilwell Drilling Company (NODC)",
        max_hook_load=1000000,
        max_rotary_torque=37500,
        max_rotary_speed=250,
        drawworks_power=2000,
        mud_pump_1_type="NOV 14-P-220 Triplex",
        mud_pump_1_hp=1600,
        mud_pump_1_liner=6.5,
        mud_pump_1_max_pressure=5200,
        mud_pump_1_max_flow=880,
        mud_pump_2_type="NOV 14-P-220 Triplex",
        mud_pump_2_hp=1600,
        mud_pump_2_liner=6.5,
        mud_pump_2_max_pressure=5200,
        mud_pump_2_max_flow=880,
        mud_pump_3_type="NOV 14-P-220 Triplex (Standby/Cement)",
        mud_pump_3_hp=1600,
        top_drive=True,
        top_drive_model="NOV TDS-11SA (AC/VFD)",
        top_drive_torque=37500,
        derrick_height=147,
        substructure_height=30,
        rotary_table_size=37.5,
        pit_volume_total=2200,
        pit_volume_active=1400,
        shale_shaker_count=4,
        degasser_type="Centrifugal Degasser (Derrick) + Atmospheric Degasser",
        desander_desilter="12\" Desander (2x) + 4\" Desilter (8x) + Mud Cleaner",
        centrifuge="2x Derrick DE-1000 Decanting Centrifuge (parallel operation)",
        generators="4x CAT 3512B DITA (1500 kW each) + 1x CAT 3508 (standby)",
        total_power=6000,
        crane_capacity=50,
        accommodation=130,
        mast_capability="API 4F - 1,000,000 lbs hook load rating, "
                        "147 ft mast, setback 450,000 lbs",
        remarks="AC/VFD Electric Rig - SCR eliminated.\n"
                "Auto-driller: NOV NOVOS drilling automation system.\n"
                "Pipe handling: NOV AR-3200 Iron Roughneck + "
                "Varco ST-120 pipe racker.\n"
                "Well monitoring: Pason EDR (Electronic Drilling Recorder).\n"
                "Rig certified for H₂S operations (NACE trim BOP stack).\n"
                "Weight indicator: Martin Decker E6-HT.\n"
                "Deadline anchor: Derrick DLA-37.5.\n"
                "Drilling line: 1-1/2\" IWRC 6x19 class.\n"
                "BOP handling: Cameron BOP transporter/trolley system.\n"
                "All certificates current (API, IADC, local authority)."
    )

    # ================================================================
    # 12. TIME ESTIMATES
    # ================================================================
    project.time_estimates = [
        TimeEstimate(
            section_name="Pre-Spud",
            operation="Rig Move, Setup, Acceptance, Pre-Spud Meeting",
            depth_from=0, depth_to=0,
            total_section_days=4.0, cumulative_days=4.0,
            remarks="Includes rig inspection, BOP function test, "
                    "equipment verification"
        ),
        TimeEstimate(
            section_name="Conductor",
            operation="Drill 36\" & Set 30\" Conductor @ 300 ft",
            depth_from=0, depth_to=300,
            rop_average=30,
            total_section_days=2.0, cumulative_days=6.0,
            remarks="Drill/drive conductor, cement, WOC, "
                    "install wellhead housing"
        ),
        TimeEstimate(
            section_name="Surface",
            operation="Drill 26\" Hole & Run/Cement 20\" Casing @ 2900 ft",
            depth_from=300, depth_to=2900,
            rop_average=35,
            total_section_days=8.0, cumulative_days=14.0,
            remarks="Drill out conductor, drill 26\" to 2900 ft, "
                    "wiper trip, run & cement 20\" casing, "
                    "WOC, nipple up BOP, drill out shoe, LOT"
        ),
        TimeEstimate(
            section_name="Intermediate - Build",
            operation="Drill 17-1/2\" Hole (Build Section: 2900-5467 ft)",
            depth_from=2900, depth_to=5467,
            rop_average=18,
            total_section_days=10.0, cumulative_days=24.0,
            remarks="KOP at 4200 ft, build 3°/100ft to 38° inc. "
                    "Lost circulation expected in UER (4800-5200 ft). "
                    "Includes LCM treatments and wiper trips."
        ),
        TimeEstimate(
            section_name="Intermediate - Hold",
            operation="Drill 17-1/2\" Hole (Tangent: 5467-10200 ft)",
            depth_from=5467, depth_to=10200,
            rop_average=15,
            total_section_days=16.0, cumulative_days=40.0,
            remarks="Tangent drilling at 38°. Hard drilling in Simsima/Aruma. "
                    "BHA change at ~7200 ft. "
                    "Wiper trips and logging included."
        ),
        TimeEstimate(
            section_name="Intermediate - Casing",
            operation="Run & Cement 13-3/8\" Casing @ 10,200 ft",
            depth_from=10200, depth_to=10200,
            total_section_days=5.0, cumulative_days=45.0,
            remarks="Condition hole, POOH, run casing, cement, WOC, "
                    "nipple up BOP, drill out shoe, LOT, CBL/VDL"
        ),
        TimeEstimate(
            section_name="Production",
            operation="Drill 12-1/4\" Hole & Run/Cement 9-5/8\" @ 14,850 ft",
            depth_from=10200, depth_to=14850,
            rop_average=10,
            total_section_days=28.0, cumulative_days=73.0,
            remarks="Convert to OBM at shoe. "
                    "RSS drilling through reservoir. "
                    "H₂S zone - full safety protocol. "
                    "Includes logging (GR-RES-DEN-NEU-SON-FMI-MDT), "
                    "coring (100 ft conventional core in Arab-D), "
                    "casing running, cementing, WOC, CBL/CBIL. "
                    "Two bit runs planned."
        ),
        TimeEstimate(
            section_name="Completion",
            operation="Completion & Well Testing",
            depth_from=14850, depth_to=14850,
            total_section_days=10.0, cumulative_days=83.0,
            remarks="Run completion string, perforate, "
                    "flow test, well clean-up, "
                    "install Xmas tree, rig down BOP"
        ),
        TimeEstimate(
            section_name="Rig Down",
            operation="Rig Release & Rig Down",
            depth_from=0, depth_to=0,
            total_section_days=2.0, cumulative_days=85.0,
            remarks="Final documentation, rig release, demobilization"
        ),
    ]

    # ================================================================
    # 13. DRILLING PARAMETERS
    # ================================================================
    project.drilling_parameters = [
        DrillingParameters(
            section_name="Surface", hole_size=26,
            depth_from=300, depth_to=2900,
            wob_min=15, wob_max=35,
            rpm_min=80, rpm_max=120,
            flow_rate_min=900, flow_rate_max=1100,
            torque_max=25000, rop_min=20, rop_max=60, rop_average=35,
            spp_max=2500, overpull_limit=50,
            pickup_weight=0, slackoff_weight=0, rotating_weight=0,
            max_ecd=14.5,
            max_trip_speed_in=5, max_trip_speed_out=5,
            remarks="Controlled ROP < 60 ft/hr in top 400 ft. "
                    "Watch for lost returns in Dammam."
        ),
        DrillingParameters(
            section_name="Intermediate (Build)", hole_size=17.5,
            depth_from=2900, depth_to=5467,
            wob_min=15, wob_max=35,
            rpm_min=0, rpm_max=160,
            flow_rate_min=700, flow_rate_max=850,
            torque_max=35000, rop_min=10, rop_max=30, rop_average=18,
            spp_max=3500, overpull_limit=50,
            max_ecd=16.0,
            max_trip_speed_in=3, max_trip_speed_out=3,
            remarks="Slide WOB: 15-25 klbs. Rotate WOB: 25-35 klbs. "
                    "Motor differential: 400-600 psi. "
                    "Monitor motor stall indicators."
        ),
        DrillingParameters(
            section_name="Intermediate (Tangent)", hole_size=17.5,
            depth_from=5467, depth_to=10200,
            wob_min=25, wob_max=45,
            rpm_min=120, rpm_max=180,
            flow_rate_min=750, flow_rate_max=900,
            torque_max=38000, rop_min=8, rop_max=25, rop_average=15,
            spp_max=4000, overpull_limit=50,
            max_ecd=16.5,
            max_trip_speed_in=3, max_trip_speed_out=3,
            remarks="Hard drilling in Simsima/Aruma (8-15 ft/hr). "
                    "Monitor bit wear. PDC bit runs ~150-200 hrs."
        ),
        DrillingParameters(
            section_name="Production", hole_size=12.25,
            depth_from=10200, depth_to=14850,
            wob_min=8, wob_max=25,
            rpm_min=120, rpm_max=200,
            flow_rate_min=550, flow_rate_max=700,
            torque_max=28000, rop_min=5, rop_max=20, rop_average=10,
            spp_max=4500, overpull_limit=40,
            max_ecd=17.2,
            max_trip_speed_in=2, max_trip_speed_out=2,
            remarks="⚠ H₂S ZONE. RSS minimum flow: 600 GPM. "
                    "MSE optimization for ROP. "
                    "Minimize overbalance (< 500 psi over PP). "
                    "Monitor ECD continuously - narrow MW window. "
                    "Max trip speed reduced for surge/swab control."
        ),
    ]

    return project


# ============================================================================
# MAIN EXECUTION - GENERATE DOCUMENT
# ============================================================================

def main():
    """تولید سند حرفه‌ای"""
    print("\n" + "=" * 70)
    print("  🛢️  PROFESSIONAL DRILLING PROGRAM GENERATOR")
    print("  Generating realistic Middle East development well document...")
    print("=" * 70 + "\n")

    # Create output directory
    Path("output").mkdir(exist_ok=True)

    # Create project
    print("📋 Step 1: Creating professional project data...")
    project = create_professional_project()
    print(f"   ✅ Well: {project.company_info.well_name}")
    print(f"   ✅ Field: {project.company_info.field_name}")
    print(f"   ✅ TD: {project.well_info.total_depth_md:,.0f} ft MD / "
          f"{project.well_info.total_depth_tvd:,.0f} ft TVD")
    print(f"   ✅ Formations: {len(project.formation_tops)} tops defined")
    print(f"   ✅ Hazards: {len(project.hazards)} risks identified")
    print(f"   ✅ Casing: {len(project.casing_design)} strings")
    print(f"   ✅ Cement: {len(project.cement_design)} jobs")
    print(f"   ✅ BHA: {len(project.bha_designs)} assemblies")
    print(f"   ✅ Mud: {len(project.mud_programs)} sections")
    print(f"   ✅ Est. Duration: {project.time_estimates[-1].cumulative_days:.0f} days")

    # Generate document
    output_file = (
        f"output/Drilling_Program_"
        f"{project.company_info.well_name.replace('-', '_')}_"
        f"Rev{project.company_info.revision}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    )

    print(f"\n📄 Step 2: Generating Word document...")
    print(f"   Output: {output_file}")

    try:
        # Try full generation with appendices
        from word_generator import DrillingProgramWordGenerator
        generator = DrillingProgramWordGenerator(project)
        generator.generate(output_file)

        # Add appendices
        try:
            from advanced_modules import AppendixGenerator
            from docx import Document

            print("📎 Step 3: Adding appendices...")
            doc = Document(output_file)
            appendix_gen = AppendixGenerator(project)
            appendix_gen.generate_all_appendices(doc)
            doc.save(output_file)
            print("   ✅ Appendices added successfully")
        except ImportError:
            print("   ⚠️ Appendix module not found - generating without appendices")

        print(f"\n{'=' * 70}")
        print(f"  ✅ DOCUMENT GENERATED SUCCESSFULLY!")
        print(f"{'=' * 70}")
        print(f"\n  📁 File: {output_file}")
        print(f"\n  📑 Document Contents:")
        print(f"     • Professional Cover Page")
        print(f"     • Revision History & Approval Signatures")
        print(f"     • Table of Contents")
        print(f"     • Abbreviations ({70}+ industry terms)")
        print(f"     • Executive Summary")
        print(f"     • Well Information (General, Location, Reservoir)")
        print(f"     • Rig Specifications (NODC RIG-112)")
        print(f"     • Formation Prognosis ({len(project.formation_tops)} formations)")
        print(f"     • Hazard Analysis ({len(project.hazards)} risks + Risk Matrix)")
        print(f"     • Casing Design ({len(project.casing_design)} strings + Design Factors)")
        print(f"     • Drilling Fluid Program ({len(project.mud_programs)} systems)")
        print(f"     • BHA & Drill String ({len(project.bha_designs)} assemblies)")
        print(f"     • Hydraulics Analysis")
        print(f"     • Cementing Program ({len(project.cement_design)} jobs)")
        print(f"     • Directional Drilling Plan (J-Type, 38°/42.5°)")
        print(f"     • BOP & Well Control (10K, Quad Ram)")
        print(f"     • Time vs Depth Estimate ({project.time_estimates[-1].cumulative_days:.0f} days)")
        print(f"     • 25+ Detailed Operating Procedures")
        print(f"     • Emergency Procedures (H₂S, Fire, Well Control)")
        print(f"     • Appendices (Kill Sheet, Trip Sheet, etc.)")
        print(f"\n  Total estimated pages: 150-200+")
        print(f"{'=' * 70}\n")

        # Open file
        if sys.platform == 'win32':
            os.startfile(output_file)
            print("  📖 Opening document in Microsoft Word...")
        elif sys.platform == 'darwin':
            os.system(f'open "{output_file}"')
        else:
            os.system(f'xdg-open "{output_file}"')

    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("   Make sure all 5 files are in the same directory:")
        print("   - main.py")
        print("   - engineering_calculations.py")
        print("   - word_generator.py")
        print("   - advanced_modules.py")
        print("   - preset_professional.py (this file)")
        print(f"\n   Required packages: pip install python-docx PySide6")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()