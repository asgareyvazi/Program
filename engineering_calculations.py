# ============================================================================
# DRILLING PROGRAM & PROCEDURE GENERATOR - PROFESSIONAL EDITION
# Version 3.0
# File: engineering_calculations.py (Part 2 of 5)
# Engineering Calculations & Procedure Generator
# ============================================================================

import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

# Import data models from Part 1
# from main import (WellProject, CasingDesign, MudProgram, BHADesign,
#                    CementDesign, FormationTop, HazardEntry, BOPStack,
#                    WellControlData, DirectionalPlan, DrillingParameters,
#                    RigSpecification, HydraulicsData, TimeEstimate)


# ============================================================================
# UNIT CONVERSION UTILITIES
# ============================================================================

class UnitConverter:
    """ابزار تبدیل واحدها"""

    @staticmethod
    def psi_to_kpa(psi: float) -> float:
        return psi * 6.89476

    @staticmethod
    def kpa_to_psi(kpa: float) -> float:
        return kpa / 6.89476

    @staticmethod
    def ft_to_m(ft: float) -> float:
        return ft * 0.3048

    @staticmethod
    def m_to_ft(m: float) -> float:
        return m / 0.3048

    @staticmethod
    def bbl_to_m3(bbl: float) -> float:
        return bbl * 0.158987

    @staticmethod
    def m3_to_bbl(m3: float) -> float:
        return m3 / 0.158987

    @staticmethod
    def ppg_to_sg(ppg: float) -> float:
        return ppg / 8.33

    @staticmethod
    def sg_to_ppg(sg: float) -> float:
        return sg * 8.33

    @staticmethod
    def ppg_to_psi_per_ft(ppg: float) -> float:
        return ppg * 0.052

    @staticmethod
    def gpm_to_lpm(gpm: float) -> float:
        return gpm * 3.78541

    @staticmethod
    def lbf_to_kn(lbf: float) -> float:
        return lbf * 0.00444822

    @staticmethod
    def ftlbs_to_nm(ftlbs: float) -> float:
        return ftlbs * 1.35582

    @staticmethod
    def fahrenheit_to_celsius(f: float) -> float:
        return (f - 32) * 5 / 9

    @staticmethod
    def celsius_to_fahrenheit(c: float) -> float:
        return c * 9 / 5 + 32

    @staticmethod
    def inches_to_mm(inches: float) -> float:
        return inches * 25.4

    @staticmethod
    def ppf_to_kg_per_m(ppf: float) -> float:
        return ppf * 1.48816


# ============================================================================
# HYDRAULICS CALCULATIONS (API RP 13D)
# ============================================================================

class HydraulicsCalculator:
    """محاسبات هیدرولیکی بر اساس API RP 13D"""

    @staticmethod
    def annular_velocity(flow_rate_gpm: float, hole_id: float,
                         pipe_od: float) -> float:
        """سرعت حلقوی (ft/min)"""
        if hole_id <= pipe_od:
            return 0
        area = (hole_id ** 2 - pipe_od ** 2)
        if area <= 0:
            return 0
        return (24.5 * flow_rate_gpm) / area

    @staticmethod
    def pipe_velocity(flow_rate_gpm: float, pipe_id: float) -> float:
        """سرعت داخل لوله (ft/min)"""
        if pipe_id <= 0:
            return 0
        return (24.5 * flow_rate_gpm) / (pipe_id ** 2)

    @staticmethod
    def reynolds_number_pipe(mud_weight: float, velocity: float,
                             pipe_id: float, pv: float,
                             yp: float) -> float:
        """عدد رینولدز در لوله (Bingham Plastic)"""
        if pv <= 0:
            return 0
        # Convert velocity from ft/min to ft/s
        v_fps = velocity / 60
        re = (928 * mud_weight * v_fps * pipe_id) / pv
        return re

    @staticmethod
    def reynolds_number_annular(mud_weight: float, velocity: float,
                                hole_id: float, pipe_od: float,
                                pv: float) -> float:
        """عدد رینولدز در حلقوی"""
        if pv <= 0:
            return 0
        d_hyd = hole_id - pipe_od
        v_fps = velocity / 60
        re = (928 * mud_weight * v_fps * d_hyd) / pv
        return re

    @staticmethod
    def pressure_loss_pipe_laminar(pv: float, velocity: float,
                                   length: float, pipe_id: float,
                                   yp: float) -> float:
        """افت فشار لوله - جریان آرام (psi)"""
        if pipe_id <= 0:
            return 0
        v_fps = velocity / 60
        dp = (pv * v_fps * length) / (1500 * pipe_id ** 2) + \
             (yp * length) / (225 * pipe_id)
        return dp

    @staticmethod
    def pressure_loss_pipe_turbulent(mud_weight: float, velocity: float,
                                      length: float, pipe_id: float,
                                      pv: float) -> float:
        """افت فشار لوله - جریان متلاطم (psi)"""
        if pipe_id <= 0:
            return 0
        v_fps = velocity / 60
        dp = (mud_weight ** 0.75 * v_fps ** 1.75 * pv ** 0.25 * length) / \
             (1396 * pipe_id ** 1.25)
        return dp

    @staticmethod
    def pressure_loss_annular_laminar(pv: float, velocity: float,
                                       length: float, hole_id: float,
                                       pipe_od: float, yp: float) -> float:
        """افت فشار حلقوی - جریان آرام (psi)"""
        d_hyd = hole_id - pipe_od
        if d_hyd <= 0:
            return 0
        v_fps = velocity / 60
        dp = (pv * v_fps * length) / (1000 * d_hyd ** 2) + \
             (yp * length) / (200 * d_hyd)
        return dp

    @staticmethod
    def pressure_loss_annular_turbulent(mud_weight: float, velocity: float,
                                         length: float, hole_id: float,
                                         pipe_od: float, pv: float) -> float:
        """افت فشار حلقوی - جریان متلاطم (psi)"""
        d_hyd = hole_id - pipe_od
        if d_hyd <= 0:
            return 0
        v_fps = velocity / 60
        dp = (mud_weight ** 0.75 * v_fps ** 1.75 * pv ** 0.25 * length) / \
             (1396 * d_hyd ** 1.25)
        return dp

    @staticmethod
    def bit_pressure_drop(flow_rate_gpm: float, mud_weight: float,
                          tfa_sqin: float) -> float:
        """افت فشار مته (psi)"""
        if tfa_sqin <= 0:
            return 0
        dp = (156.5 * mud_weight * flow_rate_gpm ** 2) / \
             (12032 * tfa_sqin ** 2)
        return dp

    @staticmethod
    def nozzle_velocity(flow_rate_gpm: float, tfa_sqin: float) -> float:
        """سرعت نازل (ft/s)"""
        if tfa_sqin <= 0:
            return 0
        return (0.3208 * flow_rate_gpm) / tfa_sqin

    @staticmethod
    def hydraulic_horsepower(flow_rate_gpm: float,
                              pressure_drop: float) -> float:
        """توان هیدرولیکی (HP)"""
        return (flow_rate_gpm * pressure_drop) / 1714

    @staticmethod
    def hsi(flow_rate_gpm: float, pressure_drop: float,
            bit_size: float) -> float:
        """شاخص توان هیدرولیکی ویژه (HP/sq.in)"""
        if bit_size <= 0:
            return 0
        bit_area = math.pi * (bit_size / 2) ** 2
        hhp = (flow_rate_gpm * pressure_drop) / 1714
        return hhp / bit_area

    @staticmethod
    def impact_force(flow_rate_gpm: float, mud_weight: float,
                     nozzle_vel: float) -> float:
        """نیروی ضربه‌ای (lbs)"""
        return (mud_weight * flow_rate_gpm * nozzle_vel) / 1932.7

    @staticmethod
    def tfa_from_nozzles(nozzles: str) -> float:
        """محاسبه TFA از نازل‌ها
        Input format: '3x14, 2x13' or '14,14,14,13,13'
        Nozzle sizes in 32nds of an inch
        """
        total_tfa = 0
        try:
            parts = nozzles.replace(' ', '').split(',')
            for part in parts:
                if 'x' in part.lower():
                    count, size = part.lower().split('x')
                    count = int(count)
                    size = float(size)
                    total_tfa += count * math.pi * (size / 32 / 2) ** 2
                else:
                    size = float(part)
                    total_tfa += math.pi * (size / 32 / 2) ** 2
        except (ValueError, ZeroDivisionError):
            pass
        return round(total_tfa, 4)

    @staticmethod
    def ecd(mud_weight: float, annular_pressure_loss: float,
            tvd: float) -> float:
        """چگالی معادل گردشی (ppg)"""
        if tvd <= 0:
            return mud_weight
        return mud_weight + annular_pressure_loss / (0.052 * tvd)

    @staticmethod
    def surge_pressure(mud_weight: float, velocity: float,
                       pv: float, yp: float, hole_id: float,
                       pipe_od: float, length: float,
                       is_open_ended: bool = True) -> float:
        """فشار سرج (psi) - تقریبی"""
        clinging_factor = 0.45 if is_open_ended else 0.6
        d_hyd = hole_id - pipe_od
        if d_hyd <= 0:
            return 0
        v_surge = velocity * clinging_factor
        # Simplified Bingham model
        dp = (pv * v_surge * length) / (60000 * d_hyd ** 2) + \
             (yp * length) / (200 * d_hyd)
        return dp

    @staticmethod
    def swab_pressure(mud_weight: float, velocity: float,
                      pv: float, yp: float, hole_id: float,
                      pipe_od: float, length: float,
                      is_open_ended: bool = True) -> float:
        """فشار سوآب (psi) - تقریبی"""
        return HydraulicsCalculator.surge_pressure(
            mud_weight, velocity, pv, yp, hole_id, pipe_od,
            length, is_open_ended
        )

    @staticmethod
    def cutting_transport_efficiency(annular_velocity: float,
                                      cutting_slip_velocity: float) -> float:
        """راندمان انتقال خرده‌ها (%)"""
        if annular_velocity <= 0:
            return 0
        transport_ratio = 1 - (cutting_slip_velocity / annular_velocity)
        return max(0, transport_ratio * 100)

    @staticmethod
    def cutting_slip_velocity(mud_weight: float, cutting_density: float,
                               cutting_diameter: float,
                               pv: float, yp: float) -> float:
        """سرعت لغزش خرده (ft/min) - Chien correlation"""
        if cutting_density <= mud_weight:
            return 0
        delta_rho = cutting_density - mud_weight
        # Simplified Moore correlation
        vs = 113.4 * cutting_diameter * math.sqrt(
            delta_rho / mud_weight
        )
        return vs

    @staticmethod
    def surface_equipment_pressure_loss(flow_rate_gpm: float,
                                         mud_weight: float,
                                         equipment_type: str = "Standard") -> float:
        """افت فشار تجهیزات سطحی (psi)"""
        # API RP 13D surface equipment constants
        if equipment_type == "Standard":
            e_constant = 5.0e-5
        elif equipment_type == "Premium":
            e_constant = 3.5e-5
        else:
            e_constant = 5.0e-5
        dp = e_constant * mud_weight * flow_rate_gpm ** 1.86
        return dp

    @staticmethod
    def calculate_full_hydraulics(
        flow_rate: float, mud_weight: float, pv: float, yp: float,
        bit_size: float, tfa: float, tvd: float,
        drill_string_sections: List[Dict],
        annular_sections: List[Dict]
    ) -> Dict:
        """محاسبه کامل هیدرولیک"""
        calc = HydraulicsCalculator

        results = {
            'flow_rate': flow_rate,
            'mud_weight': mud_weight,
        }

        # Surface equipment loss
        surface_loss = calc.surface_equipment_pressure_loss(
            flow_rate, mud_weight)
        results['surface_equipment_loss'] = round(surface_loss, 0)

        # Drillstring pressure losses
        total_ds_loss = 0
        for section in drill_string_sections:
            pipe_id = section.get('id', 0)
            length = section.get('length', 0)
            if pipe_id <= 0 or length <= 0:
                continue
            v = calc.pipe_velocity(flow_rate, pipe_id)
            re = calc.reynolds_number_pipe(mud_weight, v, pipe_id, pv, yp)
            if re < 2100:
                loss = calc.pressure_loss_pipe_laminar(
                    pv, v, length, pipe_id, yp)
            else:
                loss = calc.pressure_loss_pipe_turbulent(
                    mud_weight, v, length, pipe_id, pv)
            total_ds_loss += loss

        results['drillstring_loss'] = round(total_ds_loss, 0)

        # Bit pressure drop
        bit_loss = calc.bit_pressure_drop(flow_rate, mud_weight, tfa)
        results['bit_pressure_drop'] = round(bit_loss, 0)

        # Nozzle velocity
        nozzle_vel = calc.nozzle_velocity(flow_rate, tfa)
        results['nozzle_velocity'] = round(nozzle_vel, 1)

        # Annular pressure losses
        total_ann_loss = 0
        for section in annular_sections:
            hole_id = section.get('hole_id', 0)
            pipe_od = section.get('pipe_od', 0)
            length = section.get('length', 0)
            if hole_id <= pipe_od or length <= 0:
                continue
            v = calc.annular_velocity(flow_rate, hole_id, pipe_od)
            re = calc.reynolds_number_annular(
                mud_weight, v, hole_id, pipe_od, pv)
            if re < 2100:
                loss = calc.pressure_loss_annular_laminar(
                    pv, v, length, hole_id, pipe_od, yp)
            else:
                loss = calc.pressure_loss_annular_turbulent(
                    mud_weight, v, length, hole_id, pipe_od, pv)
            total_ann_loss += loss

        results['annular_loss'] = round(total_ann_loss, 0)

        # Total SPP
        total_spp = surface_loss + total_ds_loss + bit_loss + total_ann_loss
        results['total_spp'] = round(total_spp, 0)

        # ECD
        ecd_val = calc.ecd(mud_weight, total_ann_loss, tvd)
        results['ecd'] = round(ecd_val, 2)

        # HSI
        hsi_val = calc.hsi(flow_rate, bit_loss, bit_size)
        results['hsi'] = round(hsi_val, 2)

        # Impact Force
        impact = calc.impact_force(flow_rate, mud_weight, nozzle_vel)
        results['impact_force'] = round(impact, 0)

        # Hydraulic HP at bit
        hhp = calc.hydraulic_horsepower(flow_rate, bit_loss)
        results['bit_hhp'] = round(hhp, 1)

        # Percentage at bit
        if total_spp > 0:
            results['percent_at_bit'] = round(
                (bit_loss / total_spp) * 100, 1)
        else:
            results['percent_at_bit'] = 0

        return results


# ============================================================================
# TORQUE & DRAG CALCULATIONS
# ============================================================================

class TorqueDragCalculator:
    """محاسبات تورک و درگ"""

    @staticmethod
    def buoyancy_factor(mud_weight: float, steel_density: float = 65.5) -> float:
        """ضریب شناوری"""
        sg = mud_weight / 8.33
        return 1 - (sg * 8.33 / steel_density)

    @staticmethod
    def effective_weight(air_weight_ppf: float, length: float,
                         buoyancy: float) -> float:
        """وزن مؤثر (lbs)"""
        return air_weight_ppf * length * buoyancy

    @staticmethod
    def drag_force(normal_force: float, friction_coefficient: float) -> float:
        """نیروی اصطکاک (lbs)"""
        return normal_force * friction_coefficient

    @staticmethod
    def hook_load_tripping_out(
        sections: List[Dict],
        mud_weight: float,
        friction_coeff_oh: float = 0.30,
        friction_coeff_cased: float = 0.20
    ) -> float:
        """بار قلاب هنگام بیرون کشیدن (lbs)"""
        buoyancy = TorqueDragCalculator.buoyancy_factor(mud_weight)
        total_load = 0

        for section in sections:
            weight = section.get('weight_ppf', 0)
            length = section.get('length', 0)
            inclination = math.radians(section.get('inclination', 0))
            is_cased = section.get('is_cased', False)
            ff = friction_coeff_cased if is_cased else friction_coeff_oh

            # Simplified T&D for straight sections
            buoyed_weight = weight * length * buoyancy
            axial_component = buoyed_weight * math.cos(inclination)
            normal_component = buoyed_weight * math.sin(inclination)
            drag = normal_component * ff

            total_load += axial_component + drag

        return total_load

    @staticmethod
    def hook_load_tripping_in(
        sections: List[Dict],
        mud_weight: float,
        friction_coeff_oh: float = 0.30,
        friction_coeff_cased: float = 0.20
    ) -> float:
        """بار قلاب هنگام فرستادن (lbs)"""
        buoyancy = TorqueDragCalculator.buoyancy_factor(mud_weight)
        total_load = 0

        for section in sections:
            weight = section.get('weight_ppf', 0)
            length = section.get('length', 0)
            inclination = math.radians(section.get('inclination', 0))
            is_cased = section.get('is_cased', False)
            ff = friction_coeff_cased if is_cased else friction_coeff_oh

            buoyed_weight = weight * length * buoyancy
            axial_component = buoyed_weight * math.cos(inclination)
            normal_component = buoyed_weight * math.sin(inclination)
            drag = normal_component * ff

            total_load += axial_component - drag

        return max(0, total_load)

    @staticmethod
    def surface_torque(
        sections: List[Dict],
        mud_weight: float,
        wob: float = 0,
        friction_coeff_oh: float = 0.30,
        friction_coeff_cased: float = 0.20
    ) -> float:
        """تورک سطحی (ft-lbs) - تقریبی"""
        buoyancy = TorqueDragCalculator.buoyancy_factor(mud_weight)
        total_torque = 0

        for section in sections:
            weight = section.get('weight_ppf', 0)
            length = section.get('length', 0)
            od = section.get('od', 0)
            inclination = math.radians(section.get('inclination', 0))
            is_cased = section.get('is_cased', False)
            ff = friction_coeff_cased if is_cased else friction_coeff_oh

            buoyed_weight = weight * length * buoyancy
            normal_force = buoyed_weight * math.sin(inclination)
            drag_torque = normal_force * ff * (od / 24)  # radius in ft

            total_torque += drag_torque

        return total_torque

    @staticmethod
    def critical_buckling_load(pipe_od: float, pipe_id: float,
                                clearance: float, mud_weight: float,
                                inclination: float) -> float:
        """بار بحرانی کمانش (lbs) - Dawson-Paslay"""
        E = 30e6  # Young's modulus for steel (psi)
        I = math.pi / 64 * (pipe_od ** 4 - pipe_id ** 4)  # in^4
        weight_per_inch = 0  # Simplified
        buoyancy = TorqueDragCalculator.buoyancy_factor(mud_weight)
        w = weight_per_inch * buoyancy
        inc_rad = math.radians(inclination)

        if clearance <= 0 or math.sin(inc_rad) == 0:
            return float('inf')

        r = clearance / 2  # radial clearance in inches

        F_critical = 2 * math.sqrt(E * I * w * math.sin(inc_rad) / r)
        return F_critical


# ============================================================================
# CEMENT VOLUME CALCULATIONS
# ============================================================================

class CementCalculator:
    """محاسبات سیمانکاری"""

    @staticmethod
    def annular_volume(hole_id: float, casing_od: float,
                       length: float) -> float:
        """حجم حلقوی (bbl)"""
        if hole_id <= casing_od:
            return 0
        vol = (hole_id ** 2 - casing_od ** 2) * length / 1029.4
        return vol

    @staticmethod
    def pipe_volume(pipe_id: float, length: float) -> float:
        """حجم داخل لوله (bbl)"""
        return (pipe_id ** 2) * length / 1029.4

    @staticmethod
    def pipe_displacement(pipe_od: float, pipe_id: float,
                          length: float) -> float:
        """جابجایی لوله (bbl)"""
        return (pipe_od ** 2 - pipe_id ** 2) * length / 1029.4

    @staticmethod
    def cement_volume_with_excess(annular_volume: float,
                                   excess_percent: float) -> float:
        """حجم سیمان با مازاد (bbl)"""
        return annular_volume * (1 + excess_percent / 100)

    @staticmethod
    def number_of_sacks(slurry_volume_bbl: float,
                        yield_cuft_per_sack: float) -> float:
        """تعداد کیسه سیمان"""
        if yield_cuft_per_sack <= 0:
            return 0
        volume_cuft = slurry_volume_bbl * 5.615  # bbl to cu ft
        return volume_cuft / yield_cuft_per_sack

    @staticmethod
    def displacement_volume(casing_id: float, shoe_depth: float,
                            float_collar_depth: float) -> float:
        """حجم جابجایی (bbl)"""
        length = shoe_depth - float_collar_depth
        if length <= 0:
            return 0
        return CementCalculator.pipe_volume(casing_id, length)

    @staticmethod
    def hydrostatic_pressure(density_ppg: float, tvd: float) -> float:
        """فشار هیدرواستاتیکی (psi)"""
        return 0.052 * density_ppg * tvd

    @staticmethod
    def ecd_during_cementing(mud_weight: float, cement_density: float,
                              cement_top_tvd: float, shoe_tvd: float,
                              total_annular_pl: float) -> float:
        """ECD در حین سیمانکاری (ppg)"""
        if shoe_tvd <= 0:
            return 0
        cement_height = shoe_tvd - cement_top_tvd
        mud_height = cement_top_tvd

        hp_cement = 0.052 * cement_density * cement_height
        hp_mud = 0.052 * mud_weight * mud_height
        total_hp = hp_cement + hp_mud + total_annular_pl

        return total_hp / (0.052 * shoe_tvd)

    @staticmethod
    def plug_bump_pressure(cement_density: float, mud_weight: float,
                            shoe_tvd: float,
                            additional_pressure: float = 500) -> float:
        """فشار بامپ پلاگ (psi)"""
        differential = 0.052 * (cement_density - mud_weight) * shoe_tvd
        return differential + additional_pressure

    @staticmethod
    def calculate_full_cement_job(
        hole_size: float, casing_od: float, casing_id: float,
        shoe_depth_md: float, shoe_depth_tvd: float,
        toc_md: float, toc_tvd: float,
        float_collar_depth: float,
        lead_density: float, lead_yield: float,
        tail_density: float, tail_yield: float,
        tail_length: float,  # ft above shoe
        excess_percent: float,
        mud_weight: float
    ) -> Dict:
        """محاسبه کامل سیمانکاری"""
        calc = CementCalculator
        results = {}

        # Annular volumes
        total_ann_length = shoe_depth_md - toc_md
        tail_ann_length = min(tail_length, total_ann_length)
        lead_ann_length = total_ann_length - tail_ann_length

        lead_ann_vol = calc.annular_volume(
            hole_size, casing_od, lead_ann_length)
        tail_ann_vol = calc.annular_volume(
            hole_size, casing_od, tail_ann_length)

        # Apply excess
        lead_vol = calc.cement_volume_with_excess(
            lead_ann_vol, excess_percent)
        tail_vol = calc.cement_volume_with_excess(
            tail_ann_vol, excess_percent)

        # Shoe track volume (float collar to shoe)
        shoe_track_length = shoe_depth_md - float_collar_depth
        shoe_track_vol = calc.pipe_volume(casing_id, shoe_track_length)

        # Total cement volume
        total_cement_vol = lead_vol + tail_vol + shoe_track_vol

        # Number of sacks
        lead_sacks = calc.number_of_sacks(lead_vol, lead_yield)
        tail_sacks = calc.number_of_sacks(
            tail_vol + shoe_track_vol, tail_yield)

        # Displacement volume
        disp_vol = calc.pipe_volume(
            casing_id, float_collar_depth)

        # Pressures
        bump_pressure = calc.plug_bump_pressure(
            tail_density, mud_weight, shoe_depth_tvd)

        results = {
            'lead_annular_length': round(lead_ann_length, 0),
            'tail_annular_length': round(tail_ann_length, 0),
            'lead_annular_volume': round(lead_ann_vol, 1),
            'tail_annular_volume': round(tail_ann_vol, 1),
            'lead_volume_with_excess': round(lead_vol, 1),
            'tail_volume_with_excess': round(tail_vol, 1),
            'shoe_track_volume': round(shoe_track_vol, 1),
            'total_cement_volume': round(total_cement_vol, 1),
            'lead_sacks': round(lead_sacks, 0),
            'tail_sacks': round(tail_sacks, 0),
            'total_sacks': round(lead_sacks + tail_sacks, 0),
            'displacement_volume': round(disp_vol, 1),
            'plug_bump_pressure': round(bump_pressure, 0),
            'excess_percent': excess_percent,
        }

        return results


# ============================================================================
# CASING DESIGN CALCULATIONS (API 5C3 / ISO 10400)
# ============================================================================

class CasingDesignCalculator:
    """محاسبات طراحی لوله جداری"""

    @staticmethod
    def burst_pressure_internal(yield_strength: float, wall_thickness: float,
                                 od: float) -> float:
        """فشار ترکیدن داخلی - Barlow (psi)"""
        if od <= 0:
            return 0
        return (0.875 * 2 * yield_strength * wall_thickness) / od

    @staticmethod
    def collapse_pressure_api(yield_strength: float, od: float,
                               wall_thickness: float) -> float:
        """فشار خرد شدن - API (psi) - Simplified"""
        if wall_thickness <= 0:
            return 0
        dt_ratio = od / wall_thickness

        # Simplified API collapse calculation
        if dt_ratio < 12:
            # Yield strength collapse
            return 2 * yield_strength * (
                (dt_ratio - 1) / dt_ratio ** 2
            )
        elif dt_ratio < 20:
            # Plastic collapse (simplified)
            return yield_strength * (
                0.5 * (dt_ratio - 1) / dt_ratio ** 2
            )
        else:
            # Elastic collapse
            return (46.95e6) / (dt_ratio * (dt_ratio - 1) ** 2)

    @staticmethod
    def tensile_strength(yield_strength: float, od: float,
                         id_inner: float) -> float:
        """مقاومت کششی (lbs)"""
        area = math.pi / 4 * (od ** 2 - id_inner ** 2)
        return yield_strength * area

    @staticmethod
    def biaxial_burst(burst_rating: float, axial_load: float,
                      pipe_body_yield: float) -> float:
        """ترکیدن دو محوری - VME (psi)"""
        if pipe_body_yield <= 0:
            return burst_rating
        ratio = axial_load / pipe_body_yield
        factor = math.sqrt(1 - 0.75 * ratio ** 2) - 0.5 * ratio
        return burst_rating * factor

    @staticmethod
    def design_factor(rating: float, load: float) -> float:
        """ضریب طراحی"""
        if load <= 0:
            return float('inf')
        return rating / load

    @staticmethod
    def burst_load_gas_kick(pore_pressure_at_shoe: float,
                             gas_gradient: float,
                             shoe_tvd: float,
                             surface_tvd: float = 0) -> float:
        """بار ترکیدن - سناریوی لگد گاز (psi)"""
        gas_column_pressure = gas_gradient * (shoe_tvd - surface_tvd)
        surface_pressure = pore_pressure_at_shoe - gas_column_pressure
        return max(0, surface_pressure)

    @staticmethod
    def burst_load_dst(reservoir_pressure: float,
                        tubing_head_pressure: float,
                        gas_gradient: float,
                        reservoir_tvd: float) -> float:
        """بار ترکیدن - سناریوی DST (psi)"""
        gas_column = gas_gradient * reservoir_tvd
        surface_pressure = reservoir_pressure - gas_column
        return max(0, surface_pressure)

    @staticmethod
    def collapse_load_lost_returns(mud_weight: float,
                                     depth_tvd: float,
                                     lost_level_tvd: float = 0) -> float:
        """بار خرد شدن - از دست دادن گل (psi)"""
        external_pressure = 0.052 * mud_weight * depth_tvd
        internal_pressure = 0.052 * mud_weight * lost_level_tvd
        return external_pressure - internal_pressure

    @staticmethod
    def calculate_casing_design_summary(
        od: float, id_inner: float, weight_ppf: float,
        grade_yield_psi: float, setting_depth_tvd: float,
        mud_weight: float, pore_pressure: float,
        fracture_gradient: float
    ) -> Dict:
        """خلاصه طراحی لوله جداری"""
        calc = CasingDesignCalculator
        wall = (od - id_inner) / 2

        results = {}
        results['wall_thickness'] = round(wall, 4)

        # Burst
        burst = calc.burst_pressure_internal(grade_yield_psi, wall, od)
        results['burst_rating'] = round(burst, 0)

        # Collapse
        collapse = calc.collapse_pressure_api(
            grade_yield_psi, od, wall)
        results['collapse_rating'] = round(collapse, 0)

        # Tensile
        tensile = calc.tensile_strength(grade_yield_psi, od, id_inner)
        results['tensile_rating'] = round(tensile, 0)

        # Maximum burst load at surface (gas kick scenario)
        gas_gradient = 0.1  # psi/ft (gas)
        pp_at_shoe = 0.052 * pore_pressure * setting_depth_tvd
        burst_load = calc.burst_load_gas_kick(
            pp_at_shoe, gas_gradient, setting_depth_tvd)
        results['max_burst_load'] = round(burst_load, 0)

        # Collapse load at shoe (full evacuation)
        collapse_load = 0.052 * mud_weight * setting_depth_tvd
        results['max_collapse_load'] = round(collapse_load, 0)

        # Design factors
        if burst_load > 0:
            results['burst_df'] = round(burst / burst_load, 2)
        else:
            results['burst_df'] = 999

        if collapse_load > 0:
            results['collapse_df'] = round(collapse / collapse_load, 2)
        else:
            results['collapse_df'] = 999

        # String weight in air
        string_weight = weight_ppf * setting_depth_tvd
        buoyancy = TorqueDragCalculator.buoyancy_factor(mud_weight)
        buoyed_weight = string_weight * buoyancy
        results['string_weight_air'] = round(string_weight, 0)
        results['buoyed_weight'] = round(buoyed_weight, 0)

        if tensile > 0:
            results['tension_df'] = round(tensile / buoyed_weight, 2)
        else:
            results['tension_df'] = 999

        # MAASP
        frac_pressure = 0.052 * fracture_gradient * setting_depth_tvd
        hp_mud = 0.052 * mud_weight * setting_depth_tvd
        maasp = frac_pressure - hp_mud
        results['maasp'] = round(max(0, maasp), 0)

        return results


# ============================================================================
# WELL CONTROL CALCULATIONS
# ============================================================================

class WellControlCalculator:
    """محاسبات کنترل چاه"""

    @staticmethod
    def maasp(fracture_gradient: float, mud_weight: float,
              shoe_tvd: float) -> float:
        """حداکثر فشار مجاز حلقوی سطحی (psi)"""
        return 0.052 * (fracture_gradient - mud_weight) * shoe_tvd

    @staticmethod
    def kill_mud_weight(sidp: float, mud_weight: float,
                        tvd: float) -> float:
        """وزن گل کشتن (ppg)"""
        if tvd <= 0:
            return mud_weight
        return mud_weight + sidp / (0.052 * tvd)

    @staticmethod
    def initial_circulating_pressure(
        slow_pump_pressure: float,
        sidp: float
    ) -> float:
        """فشار گردشی اولیه (psi)"""
        return slow_pump_pressure + sidp

    @staticmethod
    def final_circulating_pressure(
        slow_pump_pressure: float,
        kill_mud_weight: float,
        original_mud_weight: float
    ) -> float:
        """فشار گردشی نهایی (psi)"""
        if original_mud_weight <= 0:
            return slow_pump_pressure
        return slow_pump_pressure * (
            kill_mud_weight / original_mud_weight
        )

    @staticmethod
    def kick_tolerance(
        fracture_gradient: float, mud_weight: float,
        shoe_tvd: float, td_tvd: float,
        hole_id: float, pipe_od: float,
        kick_intensity: float = 0.5  # ppg
    ) -> float:
        """تحمل لگد (bbl)"""
        maasp = WellControlCalculator.maasp(
            fracture_gradient, mud_weight, shoe_tvd)

        # Simplified kick tolerance
        ann_cap = (hole_id ** 2 - pipe_od ** 2) / 1029.4  # bbl/ft

        if kick_intensity <= 0:
            return 0

        kick_height = maasp / (0.052 * kick_intensity)
        kick_volume = kick_height * ann_cap

        return kick_volume

    @staticmethod
    def strokes_to_bit(pipe_volume: float,
                        pump_output: float) -> float:
        """تعداد ضربه تا مته"""
        if pump_output <= 0:
            return 0
        return pipe_volume / pump_output

    @staticmethod
    def strokes_from_bit_to_choke(annular_volume: float,
                                    pump_output: float) -> float:
        """تعداد ضربه از مته تا چوک"""
        if pump_output <= 0:
            return 0
        return annular_volume / pump_output

    @staticmethod
    def pressure_schedule_drillers_method(
        icp: float, fcp: float,
        strokes_to_bit: float,
        num_points: int = 10
    ) -> List[Dict]:
        """جدول فشار - روش حفار"""
        schedule = []
        step = strokes_to_bit / num_points if num_points > 0 else 1
        pressure_drop_per_stroke = (icp - fcp) / strokes_to_bit \
            if strokes_to_bit > 0 else 0

        for i in range(num_points + 1):
            strokes = i * step
            pressure = icp - (pressure_drop_per_stroke * strokes)
            schedule.append({
                'strokes': round(strokes, 0),
                'pressure': round(max(pressure, fcp), 0)
            })

        return schedule


# ============================================================================
# DRILLING ENGINEERING UTILITIES
# ============================================================================

class DrillingEngineering:
    """ابزارهای مهندسی حفاری"""

    @staticmethod
    def lot_pressure_to_gradient(lot_pressure: float, mud_weight: float,
                                  shoe_tvd: float) -> float:
        """تبدیل فشار LOT به گرادیان (ppg EMW)"""
        if shoe_tvd <= 0:
            return 0
        return mud_weight + lot_pressure / (0.052 * shoe_tvd)

    @staticmethod
    def formation_pressure_gradient(formation_pressure: float,
                                     tvd: float) -> float:
        """گرادیان فشار سازند (ppg EMW)"""
        if tvd <= 0:
            return 0
        return formation_pressure / (0.052 * tvd)

    @staticmethod
    def temperature_gradient(surface_temp: float, bottom_temp: float,
                              depth: float) -> float:
        """گرادیان دمایی (°F/100ft)"""
        if depth <= 0:
            return 0
        return (bottom_temp - surface_temp) / depth * 100

    @staticmethod
    def temperature_at_depth(surface_temp: float, gradient: float,
                              depth: float) -> float:
        """دما در عمق (°F)"""
        return surface_temp + (gradient / 100) * depth

    @staticmethod
    def pipe_stretch(free_length: float, weight_ppf: float,
                      od: float, pipe_id: float) -> float:
        """کشیدگی لوله (inches)"""
        E = 30e6  # psi
        area = math.pi / 4 * (od ** 2 - pipe_id ** 2)
        if area <= 0:
            return 0
        total_weight = weight_ppf * free_length
        average_load = total_weight / 2
        stretch = (average_load * free_length * 12) / (E * area)
        return stretch

    @staticmethod
    def minimum_flow_rate_hole_cleaning(
        hole_size: float, pipe_od: float,
        mud_weight: float, inclination: float
    ) -> float:
        """حداقل دبی برای تمیزکاری (GPM) - تقریبی"""
        annular_area = math.pi / 4 * (hole_size ** 2 - pipe_od ** 2)

        # Minimum annular velocity based on inclination
        if inclination < 30:
            min_av = 100  # ft/min for vertical
        elif inclination < 60:
            min_av = 150  # ft/min for deviated
        else:
            min_av = 180  # ft/min for horizontal

        # Q = AV * Area / 24.5
        min_q = min_av * (hole_size ** 2 - pipe_od ** 2) / 24.5
        return round(min_q, 0)

    @staticmethod
    def estimated_rop(wob: float, rpm: float, bit_size: float,
                       formation_hardness: float = 1.0) -> float:
        """ROP تخمینی (ft/hr) - مدل ساده"""
        if bit_size <= 0:
            return 0
        # Simplified Bourgoyne-Young model concept
        rop = (wob * rpm) / (bit_size * 100 * formation_hardness)
        return max(1, min(rop, 500))

    @staticmethod
    def total_well_cost(
        rig_rate_per_day: float,
        total_days: float,
        spread_cost_per_day: float,
        completion_cost: float = 0,
        logging_cost: float = 0,
        casing_cost: float = 0,
        mud_cost: float = 0,
        cement_cost: float = 0,
        bits_cost: float = 0,
        directional_cost: float = 0,
        other_cost: float = 0,
        well_depth_ft: float = 0.0
    ) -> Dict:
        """تخمین هزینه کل چاه

        well_depth_ft: depth used for cost-per-foot. When 0 (unknown),
        cost_per_foot/cost_per_meter are reported as 0 to avoid the
        previous total/1 bug.
        """
        rig_cost = rig_rate_per_day * total_days
        spread_cost = spread_cost_per_day * total_days
        tangible = casing_cost + completion_cost
        services = (logging_cost + mud_cost + cement_cost +
                    bits_cost + directional_cost)

        total = (rig_cost + spread_cost + tangible +
                 services + other_cost)

        cpf = total / well_depth_ft if (well_depth_ft and total > 0) else 0.0
        return {
            'rig_cost': rig_cost,
            'spread_cost': spread_cost,
            'tangible_cost': tangible,
            'services_cost': services,
            'other_cost': other_cost,
            'total_cost': total,
            'cost_per_foot': cpf,
            'cost_per_meter': cpf / 3.28084 if cpf else 0.0,
            'cost_per_day': total / total_days if total_days > 0 else 0
        }


# ============================================================================
# PROCEDURE GENERATOR ENGINE
# ============================================================================

class ProcedureGenerator:
    """موتور تولید پروسیجرهای حفاری"""

    def __init__(self, project):
        self.project = project
        self.procedures = {}

    def generate_all_procedures(self) -> Dict[str, List[str]]:
        """تولید تمامی پروسیجرها"""
        self.procedures = {}

        self.procedures['pre_spud'] = self.generate_pre_spud_procedure()
        self.procedures['conductor'] = self.generate_conductor_procedure()

        for casing in self.project.casing_design:
            section_key = casing.section_name.lower().replace(' ', '_')
            self.procedures[f'drill_{section_key}'] = \
                self.generate_drilling_procedure(casing)
            self.procedures[f'trip_{section_key}'] = \
                self.generate_tripping_procedure(casing)
            self.procedures[f'casing_run_{section_key}'] = \
                self.generate_casing_running_procedure(casing)
            self.procedures[f'cement_{section_key}'] = \
                self.generate_cementing_procedure(casing)

        self.procedures['bop_nipple_up'] = \
            self.generate_bop_nipple_up_procedure()
        self.procedures['bop_test'] = \
            self.generate_bop_test_procedure()
        self.procedures['lot_fit'] = \
            self.generate_lot_fit_procedure()
        self.procedures['well_control'] = \
            self.generate_well_control_procedure()
        self.procedures['kick_drill'] = \
            self.generate_kick_drill_procedure()
        self.procedures['stuck_pipe'] = \
            self.generate_stuck_pipe_procedure()
        self.procedures['lost_circulation'] = \
            self.generate_lost_circulation_procedure()
        self.procedures['fishing'] = \
            self.generate_fishing_procedure()
        self.procedures['h2s_emergency'] = \
            self.generate_h2s_procedure()
        self.procedures['wellbore_cleanup'] = \
            self.generate_wellbore_cleanup_procedure()
        self.procedures['directional'] = \
            self.generate_directional_procedure()
        self.procedures['logging'] = \
            self.generate_logging_procedure()
        self.procedures['coring'] = \
            self.generate_coring_procedure()
        self.procedures['dst'] = \
            self.generate_dst_procedure()
        self.procedures['abandonment'] = \
            self.generate_abandonment_procedure()
        self.procedures['rig_move'] = \
            self.generate_rig_move_procedure()
        self.procedures['hot_work'] = \
            self.generate_hot_work_procedure()
        self.procedures['confined_space'] = \
            self.generate_confined_space_procedure()
        self.procedures['helicopter_ops'] = \
            self.generate_helicopter_procedure()
        self.procedures['hse'] = \
            self.generate_hse_procedure()

        return self.procedures

    # ========================================================================
    # PRE-SPUD CHECKLIST
    # ========================================================================

    def generate_pre_spud_procedure(self) -> List[str]:
        ci = self.project.company_info
        wi = self.project.well_info
        rs = self.project.rig_spec

        steps = [
            "PRE-SPUD CHECKLIST AND PROCEDURE",
            "",
            "1. DOCUMENTATION VERIFICATION",
            f"   1.1. Verify all permits and licenses are in place for well {ci.well_name}.",
            "   1.2. Confirm approved Drilling Program document is on site.",
            "   1.3. Verify Environmental Impact Assessment (EIA) approval.",
            "   1.4. Confirm all regulatory notifications have been submitted.",
            "   1.5. Verify insurance certificates are current.",
            "   1.6. Confirm government representative notification.",
            "   1.7. Review all contractor certifications and competency records.",
            "",
            "2. LOCATION PREPARATION",
            f"   2.1. Verify well location coordinates: Lat {wi.surface_latitude}, "
            f"Long {wi.surface_longitude}.",
            "   2.2. Confirm location survey completed and approved.",
            "   2.3. Verify cellar/conductor pit dimensions and condition.",
            "   2.4. Confirm access road condition and load capacity.",
            "   2.5. Verify drainage system and containment berms.",
            "   2.6. Confirm water supply availability and quality.",
            "   2.7. Verify waste disposal arrangements.",
            "   2.8. Confirm power supply arrangements.",
            "",
            "3. RIG ACCEPTANCE",
            f"   3.1. Complete rig acceptance inspection for {rs.rig_name}.",
            "   3.2. Verify all rig certification documents.",
            "   3.3. Confirm third-party inspection certificates for:",
            "        a) Derrick/Mast and substructure",
            "        b) Drawworks, brake system, and crown block",
            "        c) Top drive / Rotary table",
            "        d) Drilling lines and dead line anchor",
            "        e) BOP equipment and control system",
            "        f) Mud pumps and circulating system",
            "        g) Power generation system",
            "        h) Well control equipment",
            "        i) Lifting equipment and cranes",
            f"   3.4. Verify maximum hook load capacity: "
            f"{rs.max_hook_load:,.0f} lbs.",
            f"   3.5. Verify drawworks power: {rs.drawworks_power:,.0f} HP.",
            "   3.6. Conduct ton-mile calculations for drilling line.",
            "   3.7. Verify BOP stack configuration matches program.",
            "",
            "4. WELL CONTROL EQUIPMENT",
            f"   4.1. Verify BOP stack rated for "
            f"{self.project.bop_stack.working_pressure:,.0f} psi WP.",
            f"   4.2. Confirm BOP bore size: "
            f"{self.project.bop_stack.bore_size}\".",
            "   4.3. Verify accumulator capacity and precharge pressure.",
            "   4.4. Function test all BOP rams and annular.",
            "   4.5. Verify choke manifold and kill manifold integrity.",
            "   4.6. Confirm remote BOP panel operation.",
            "   4.7. Verify diverter system installation and function.",
            "   4.8. Confirm well control monitoring equipment "
            "(pit volume totalizer, flow show, gas detectors).",
            "",
            "5. MUD SYSTEM",
            "   5.1. Verify active pit volume and reserve capacity.",
            "   5.2. Confirm solids control equipment:",
            "        a) Shale shakers operational",
            "        b) Degasser functional",
            "        c) Desander / Desilter / Mud Cleaner",
            "        d) Centrifuge (if required)",
            "   5.3. Verify mud mixing system and agitators.",
            "   5.4. Confirm mud products inventory per program.",
            "   5.5. Calibrate pit level indicators.",
            "   5.6. Verify mud gas separator (poor boy degasser).",
            "   5.7. Calibrate trip tank system.",
            "",
            "6. SAFETY SYSTEMS",
            "   6.1. Verify fire detection and fighting equipment.",
            "   6.2. Confirm emergency shutdown (ESD) system test.",
            "   6.3. Verify gas detection system calibration.",
            f"   6.4. {'Confirm H₂S detection and breathing apparatus.' if wi.expected_h2s_concentration > 0 else 'H₂S equipment N/A for this well.'}",
            "   6.5. Verify PA system and emergency alarms.",
            "   6.6. Confirm life-saving equipment (life rafts, life jackets).",
            "   6.7. Verify medical equipment and trained first aider.",
            "   6.8. Confirm emergency evacuation plan and muster stations.",
            "   6.9. Verify STOP card / hazard observation system.",
            "",
            "7. COMMUNICATIONS",
            "   7.1. Verify radio communications (VHF/UHF).",
            "   7.2. Confirm satellite phone availability.",
            "   7.3. Verify data transmission system (WITSML).",
            "   7.4. Confirm emergency contact numbers posted.",
            "   7.5. Verify weather monitoring system.",
            "",
            "8. PRE-SPUD MEETING",
            "   8.1. Conduct Pre-Spud Meeting with all crew members.",
            "   8.2. Review Drilling Program highlights.",
            "   8.3. Review HSE plan and emergency procedures.",
            "   8.4. Review well control procedures and responsibilities.",
            "   8.5. Review anti-collision plan (if applicable).",
            "   8.6. Discuss lessons learned from offset wells.",
            "   8.7. Ensure all crew have signed attendance sheet.",
            "",
            "9. FINAL CHECKS",
            "   9.1. Verify all BHA and tubular are on location.",
            "   9.2. Confirm casing inventory per program.",
            "   9.3. Verify cement and additives inventory.",
            "   9.4. Confirm all service company equipment on site.",
            "   9.5. Verify mud logging unit setup and calibrated.",
            "   9.6. Final walk-around inspection.",
            "   9.7. Obtain authorization to spud from Company Representative.",
            "",
            "10. DOCUMENTATION TO BE ON SITE",
            "   10.1. Approved Drilling Program",
            "   10.2. Well Control Manual",
            "   10.3. Emergency Response Plan",
            "   10.4. HSE Plan",
            "   10.5. Casing/Cement program details",
            "   10.6. Directional plan and surveys",
            "   10.7. API/IADC reporting forms",
            "   10.8. Contractor equipment certifications",
            "   10.9. Rig floor poster (well data)",
        ]

        return steps

    # ========================================================================
    # CONDUCTOR SETTING PROCEDURE
    # ========================================================================

    def generate_conductor_procedure(self) -> List[str]:
        conductor = None
        for c in self.project.casing_design:
            if 'conductor' in c.section_type.lower() or \
               'conductor' in c.section_name.lower():
                conductor = c
                break

        if not conductor:
            return ["No conductor section defined in casing design."]

        steps = [
            f"CONDUCTOR SETTING PROCEDURE - {conductor.casing_od}\" "
            f"@ {conductor.setting_depth_md:,.0f} ft",
            "",
            "1. PREPARATION",
            f"   1.1. Confirm {conductor.hole_size}\" hole opener / "
            f"drilling assembly is made up.",
            f"   1.2. Verify {conductor.casing_od}\" conductor pipe on "
            f"rack - Grade: {conductor.casing_grade}, "
            f"Weight: {conductor.casing_weight} ppf.",
            f"   1.3. Confirm {conductor.section_name} setting "
            f"depth: {conductor.setting_depth_md:,.0f} ft MD / "
            f"{conductor.setting_depth_tvd:,.0f} ft TVD.",
            "   1.4. Verify conductor driving equipment (if driving) or "
            "drilling equipment is ready.",
            "   1.5. Prepare spud mud as per mud program.",
            "",
            "2. SPUDDING OPERATIONS",
            "   2.1. Install diverter system.",
            f"   2.2. Pick up {conductor.hole_size}\" BHA.",
            "   2.3. Verify BHA components per program.",
            f"   2.4. Drill {conductor.hole_size}\" hole from surface to "
            f"{conductor.setting_depth_md:,.0f} ft.",
            "   2.5. Maintain controlled ROP - do not exceed "
            "maximum recommended.",
            "   2.6. Monitor returns for shallow gas indications.",
            "   2.7. If shallow gas encountered, implement "
            "diverter procedures.",
            "   2.8. Circulate and clean hole prior to POOH.",
            "   2.9. POOH and lay down BHA.",
            "",
            "3. RUNNING CONDUCTOR",
            f"   3.1. Make up float shoe on first joint of "
            f"{conductor.casing_od}\" conductor.",
            "   3.2. Make up float collar one joint above shoe.",
            f"   3.3. Run {conductor.casing_od}\" conductor to "
            f"{conductor.setting_depth_md:,.0f} ft.",
            "   3.4. Install centralizers as per program.",
            "   3.5. Fill conductor every 5 joints to prevent "
            "wet shoe.",
            "   3.6. Tag bottom and verify depth.",
            "",
            "4. CEMENTING CONDUCTOR",
            "   4.1. Circulate hole clean prior to cementing.",
            "   4.2. Pump cement per cement program.",
            "   4.3. Verify cement returns at surface.",
            "   4.4. If no returns, be prepared to top up cement "
            "from surface.",
            f"   4.5. WOC as per program.",
            "",
            "5. POST CONDUCTOR OPERATIONS",
            "   5.1. Cut and weld conductor at required height.",
            "   5.2. Install conductor housing / wellhead.",
            "   5.3. Drill out cement and float equipment.",
            "   5.4. Prepare for surface hole section.",
        ]

        return steps

    # ========================================================================
    # DRILLING PROCEDURE (PER SECTION)
    # ========================================================================

    def generate_drilling_procedure(self, casing: object) -> List[str]:
        # Find matching mud program
        mud = None
        for m in self.project.mud_programs:
            if m.section_name.lower() == casing.section_name.lower():
                mud = m
                break

        # Find matching BHA
        bha = None
        for b in self.project.bha_designs:
            if b.section_name.lower() == casing.section_name.lower():
                bha = b
                break

        # Find matching parameters
        params = None
        for p in self.project.drilling_parameters:
            if p.section_name.lower() == casing.section_name.lower():
                params = p
                break

        # Get shoe of previous section
        prev_shoe = 0
        for c in self.project.casing_design:
            if c.section_name == casing.section_name:
                break
            prev_shoe = c.setting_depth_md

        mud_type = mud.mud_type if mud else "As per program"
        mud_weight_in = f"{mud.mud_weight_in}" if mud else "TBD"
        mud_weight_out = f"{mud.mud_weight_out}" if mud else "TBD"

        bit_type = bha.bit_type if bha else "PDC"
        bit_size = f"{bha.bit_size}" if bha else f"{casing.hole_size}"
        bha_type = bha.bha_type if bha else "Rotary"

        wob_range = f"{params.wob_min}-{params.wob_max} klbs" \
            if params else "As per program"
        rpm_range = f"{params.rpm_min}-{params.rpm_max}" \
            if params else "As per program"
        flow_range = f"{params.flow_rate_min}-{params.flow_rate_max} GPM" \
            if params else "As per program"

        steps = [
            f"DRILLING PROCEDURE - {casing.section_name.upper()} SECTION",
            f"{casing.hole_size}\" Hole from "
            f"{prev_shoe:,.0f} ft to {casing.setting_depth_md:,.0f} ft MD",
            "",
            "1. PRE-DRILLING PREPARATION",
            f"   1.1. Review {casing.section_name} section "
            f"program with all crews.",
            "   1.2. Conduct pre-section toolbox talk / safety meeting.",
            f"   1.3. Prepare {mud_type} mud system.",
            f"   1.4. Target initial mud weight: {mud_weight_in} ppg.",
            f"   1.5. Verify BHA components for BHA #{bha.bha_number if bha else 1}.",
            f"   1.6. Confirm {bit_size}\" {bit_type} bit is inspected.",
            "   1.7. Verify all downhole tools:",
            f"        - BHA Type: {bha_type}",
            f"        - {'Motor: ' + bha.motor_type if bha and bha.motor_type else 'No motor required'}",
            f"        - {'RSS: ' + bha.rss_type if bha and bha.rss_type else 'No RSS required'}",
            f"        - {'MWD: ' + bha.mwd_type if bha and bha.mwd_type else 'MWD as per program'}",
            f"        - {'LWD: ' + bha.lwd_sensors if bha and bha.lwd_sensors else 'No LWD'}",
            "   1.8. Verify drilling fluid products on location.",
            "   1.9. Confirm solids control equipment is operational.",
            "   1.10. Verify mud logging unit is recording.",
            "",
            "2. BHA MAKE-UP",
            f"   2.1. Make up {bit_size}\" {bit_type} bit.",
            "   2.2. Record bit serial number and nozzle configuration.",
            "   2.3. Make up BHA components per BHA diagram.",
            "   2.4. Verify all connections are made up "
            "to recommended torque.",
            "   2.5. Verify MWD/LWD tools are initialized "
            "and communicating.",
            "   2.6. Record BHA total length and component details.",
            "   2.7. Perform MWD surface check / flow check.",
            "",
            "3. RUN IN HOLE (RIH)",
            "   3.1. RIH to previous shoe depth with pumps on.",
            f"   3.2. Observe maximum RIH speed as per program.",
            "   3.3. Record all tight spots during RIH.",
            "   3.4. Tag cement / shoe track and record depth.",
            "   3.5. Drill out cement, float equipment, and "
            "rathole.",
            "   3.6. Circulate clean and verify returns.",
            "",
            "4. LEAK-OFF TEST / FORMATION INTEGRITY TEST",
            "   4.1. Perform LOT/FIT as per procedure at shoe depth.",
            "   4.2. Record LOT/FIT result and calculate EMW.",
            "   4.3. Verify LOT/FIT result meets minimum "
            "design requirements.",
            "   4.4. Report results to office and obtain "
            "approval to proceed.",
            "",
            "5. DRILLING AHEAD",
            f"   5.1. Drill {casing.hole_size}\" hole from "
            f"{prev_shoe:,.0f} ft to {casing.setting_depth_md:,.0f} ft.",
            f"   5.2. Drilling parameters:",
            f"        - WOB: {wob_range}",
            f"        - RPM: {rpm_range}",
            f"        - Flow Rate: {flow_range}",
            f"        - Max ECD: {params.max_ecd if params else 'Monitor'} ppg",
            "   5.3. Monitor and record all drilling parameters.",
            "   5.4. Take surveys as per survey program "
            f"(every {self.project.directional_plan.survey_frequency} ft).",
            "   5.5. Verify trajectory is within planned "
            "corridor / target.",
            "   5.6. Monitor ECD continuously - do not exceed "
            "fracture gradient.",
            "   5.7. Perform connection gas / background gas "
            "monitoring.",
            "   5.8. Record ROP, torque, drag, and all parameters.",
            f"   5.9. Maintain mud weight: {mud_weight_in} - "
            f"{mud_weight_out} ppg.",
            "   5.10. Perform wiper trips as required "
            "(typically every 500-1000 ft in problem zones).",
            "",
            "6. HOLE CONDITION MONITORING",
            "   6.1. Monitor for stuck pipe indicators:",
            "        - Increasing torque / drag",
            "        - Overpull on connections",
            "        - Fill on bottom",
            "   6.2. Monitor for lost circulation indicators:",
            "        - Pit volume loss",
            "        - Reduced flow returns",
            "        - Decrease in ECD",
            "   6.3. Monitor for kick indicators:",
            "        - Pit gain",
            "        - Increased return flow",
            "        - Drilling break",
            "        - Connection gas",
            "   6.4. Monitor for wellbore stability issues:",
            "        - Cavings at shakers",
            "        - Tight hole on connections",
            "        - Increase in background gas",
            f"   6.5. Maximum overpull limit: "
            f"{params.overpull_limit if params else 50} klbs.",
            "",
            "7. REACHING SECTION TD",
            f"   7.1. Drill to section TD: "
            f"{casing.setting_depth_md:,.0f} ft MD / "
            f"{casing.setting_depth_tvd:,.0f} ft TVD.",
            "   7.2. Circulate minimum 2 x hole volume (bottoms up).",
            "   7.3. Take final survey at TD.",
            "   7.4. Perform short trip to shoe to confirm "
            "hole condition.",
            "   7.5. Condition mud for logging/casing operations.",
            f"   7.6. Target mud weight out: {mud_weight_out} ppg.",
            "   7.7. Reduce mud yield point and gel strengths "
            "for casing run.",
            "   7.8. Check and record final mud properties.",
            "",
            "8. POOH AND BIT GRADING",
            "   8.1. Circulate clean bottoms up.",
            "   8.2. POOH, pumping out of hole.",
            "   8.3. Monitor hole fill / swab at all times.",
            "   8.4. Keep hole full at all times per well control policy.",
            "   8.5. Grade bit per IADC dull bit grading system.",
            "   8.6. Lay down BHA and inspect all components.",
            "   8.7. Record all downhole tool hours and status.",
        ]

        return steps

    # ========================================================================
    # TRIPPING PROCEDURE
    # ========================================================================

    def generate_tripping_procedure(self, casing: object) -> List[str]:
        steps = [
            f"TRIPPING PROCEDURE - {casing.section_name.upper()} SECTION",
            f"({casing.hole_size}\" Hole)",
            "",
            "1. GENERAL TRIPPING REQUIREMENTS",
            "   1.1. All trips shall be monitored using trip tank.",
            "   1.2. Keep hole full at all times.",
            "   1.3. Monitor trip tank volume continuously.",
            "   1.4. Establish pump strokes to fill volume per stand.",
            "   1.5. Compare actual vs calculated fill volumes.",
            "   1.6. Any discrepancy > 3 bbl shall be investigated.",
            "",
            "2. TRIPPING OUT OF HOLE (TOOH)",
            "   2.1. Circulate bottoms up before pulling out.",
            "   2.2. Pull first 5 stands slowly to establish pattern.",
            "   2.3. Record pickup weight for each stand initially.",
            f"   2.4. Maximum trip speed out: "
            f"{casing.section_name} section - per program ft/min.",
            "   2.5. Monitor for swabbing:",
            "        a) Watch for pit level decrease",
            "        b) If pit level increases unexpectedly - STOP",
            "        c) Check for flow",
            "   2.6. Fill hole every 5 stands (or as per protocol).",
            "   2.7. Record fill volume vs theoretical.",
            "   2.8. If overpull exceeds limit:",
            "        a) Stop and work pipe",
            "        b) Attempt to circulate",
            "        c) If unsuccessful, consider pumping out",
            "   2.9. Record all tight spots and overpull values.",
            "   2.10. Ensure pipe wiper / pipe spinner used "
            "at surface.",
            "",
            "3. TRIPPING IN HOLE (TIH)",
            "   3.1. Break circulation at shoe before continuing.",
            "   3.2. RIH slowly, observing maximum RIH speed.",
            "   3.3. Monitor for surge effects:",
            "        a) Watch for pit level increase (surge)",
            "        b) Watch for flow at flowline",
            "   3.4. Fill pipe from top every 5 stands.",
            "   3.5. Record setdown weight.",
            f"   3.6. Maximum RIH speed: per program ft/min.",
            "   3.7. If resistance encountered:",
            "        a) Stop and circulate",
            "        b) Ream through tight spots",
            "        c) Do not force pipe through restrictions",
            "   3.8. Tag bottom and verify depth.",
            "   3.9. Circulate bottoms up before resuming drilling.",
            "",
            "4. WIPER TRIP PROCEDURE",
            "   4.1. Circulate bottoms up before starting.",
            "   4.2. Pull out to shoe (or last casing point).",
            "   4.3. Monitor for tight spots and record.",
            "   4.4. RIH back to bottom.",
            "   4.5. Ream through any tight spots.",
            "   4.6. Circulate bottoms up at TD.",
            "   4.7. Resume drilling operations.",
            "",
            "5. FLOW CHECK PROCEDURE",
            "   5.1. Stop pumps and observe well for flow.",
            "   5.2. Minimum observation period: 15 minutes "
            "(or per company policy).",
            "   5.3. Monitor pit levels.",
            "   5.4. If flow observed:",
            "        a) Close well in per shut-in procedure",
            "        b) Record SIDPP and SICP",
            "        c) Notify Company Representative",
            "        d) Follow well control procedures",
            "   5.5. If no flow, proceed with operations.",
            "",
            "6. TRIP MARGIN AND SAFETY",
            "   6.1. Maintain minimum trip margin of 0.2 ppg "
            "above pore pressure.",
            "   6.2. Always have backup pipe available.",
            "   6.3. Never leave open hole without adequate "
            "hydrostatic.",
            "   6.4. Record all trip data on daily report.",
        ]

        return steps

    # ========================================================================
    # CASING RUNNING PROCEDURE
    # ========================================================================

    def generate_casing_running_procedure(self, casing: object) -> List[str]:
        is_liner = casing.is_liner

        if is_liner:
            return self.generate_liner_running_procedure(casing)

        steps = [
            f"CASING RUNNING PROCEDURE - {casing.casing_od}\" "
            f"{casing.section_name.upper()} CASING",
            f"Setting Depth: {casing.setting_depth_md:,.0f} ft MD / "
            f"{casing.setting_depth_tvd:,.0f} ft TVD",
            "",
            "1. PRE-CASING RUN PREPARATION",
            f"   1.1. Verify {casing.casing_od}\" casing tally:",
            f"        - Grade: {casing.casing_grade}",
            f"        - Weight: {casing.casing_weight} ppf",
            f"        - Connection: {casing.casing_connection}",
            f"        - Drift ID: {casing.drift_id}\"",
            "   1.2. Verify all casing has been drifted.",
            "   1.3. Inspect threads on each joint.",
            "   1.4. Rack casing in running order per tally.",
            "   1.5. Verify casing accessories:",
            "        a) Float shoe (1 ea)",
            "        b) Float collar (1 ea)",
            f"        c) Centralizers ({casing.centralizer_type}, "
            f"every {casing.centralizer_spacing} ft)",
            "        d) Scratchers/wipers (if applicable)",
            "        e) Stop collars / Landing collar",
            "        f) Stage collar (if stage cementing)",
            "   1.6. Verify hole condition - wiper trip completed.",
            "   1.7. Condition mud for casing run:",
            "        - Reduce YP to minimum",
            "        - Reduce gel strengths",
            "        - Verify fluid loss < 5 ml/30min",
            "   1.8. Verify fill up line and fill up rate.",
            "   1.9. Prepare casing thread compound (API or premium).",
            "   1.10. Prepare cement equipment and products.",
            "   1.11. Conduct pre-job safety meeting.",
            "",
            "2. RUNNING CASING",
            "   2.1. Make up float shoe on first joint.",
            "   2.2. Apply thread compound per manufacturer specs.",
            "   2.3. Make up first joint to recommended torque.",
            "   2.4. RIH first joint and fill with mud.",
            f"   2.5. Install float collar at "
            f"{casing.float_collar_depth:,.0f} ft (approx. "
            f"{int((casing.setting_depth_md - casing.float_collar_depth) / 40)} "
            f"joints above shoe).",
            "   2.6. Continue running casing:",
            "        a) Apply correct thread compound to each joint",
            "        b) Make up each joint to specified torque",
            "        c) Record actual torque for each joint",
            "        d) Install centralizers per program",
            "        e) Fill casing every 5-10 joints",
            "   2.7. Monitor for drag and restrictions:",
            "        a) Record hook load continuously",
            "        b) Monitor for surging (pit gain)",
            "        c) Do not force casing through tight spots",
            "        d) If stuck, circulate and work pipe gently",
            f"   2.8. Maximum running speed: 3 ft/s "
            f"(avoid surge > ECD limit).",
            "   2.9. Reciprocate casing through known restrictions.",
            "   2.10. Record casing tally and verify total depth.",
            "",
            "3. LANDING CASING",
            f"   3.1. Land casing at {casing.setting_depth_md:,.0f} ft MD.",
            "   3.2. Verify depth with tally.",
            "   3.3. Do NOT rotate casing unless required "
            "by cement program.",
            "   3.4. Establish circulation through casing.",
            "   3.5. Circulate minimum 1 x annular volume.",
            "   3.6. Verify full returns and record circulating "
            "pressure.",
            "   3.7. Record pickup and slackoff weights.",
            "",
            "4. POST CASING RUN (PRE-CEMENT)",
            "   4.1. Verify casing fill up volume matches calculated.",
            "   4.2. Verify circulation is established.",
            "   4.3. If reciprocating/rotating during cement, "
            "establish baseline.",
            "   4.4. Verify cement head is rigged up.",
            "   4.5. Verify cement lines are tested.",
            "   4.6. Proceed to cementing procedure.",
        ]

        return steps

    def generate_liner_running_procedure(self, casing: object) -> List[str]:
        steps = [
            f"LINER RUNNING PROCEDURE - {casing.casing_od}\" "
            f"{casing.section_name.upper()} LINER",
            f"Liner Top: {casing.liner_top_md:,.0f} ft MD",
            f"Liner Shoe: {casing.setting_depth_md:,.0f} ft MD",
            f"Liner Overlap: {casing.liner_overlap:,.0f} ft",
            "",
            "1. PREPARATION",
            f"   1.1. Verify {casing.casing_od}\" liner tally.",
            "   1.2. Verify liner hanger and setting tool.",
            "   1.3. Verify PBR (Polished Bore Receptacle).",
            "   1.4. Verify liner running tool functionality.",
            "   1.5. Prepare liner assembly in mousehole.",
            "",
            "2. MAKE UP LINER STRING",
            "   2.1. Make up float shoe, float collar, and "
            "liner joints.",
            "   2.2. Install centralizers per program.",
            "   2.3. Make up liner hanger at top of string.",
            "   2.4. Make up liner running tool on drill pipe.",
            "   2.5. Record total liner length and component depths.",
            "",
            "3. RUN LINER",
            "   3.1. RIH liner on drill pipe.",
            "   3.2. Circulate at regular intervals during run.",
            "   3.3. Monitor for drag and restrictions.",
            "   3.4. Tag bottom and verify liner depth.",
            "   3.5. Circulate to clean hole.",
            "",
            "4. SET LINER HANGER",
            "   4.1. Set liner hanger at programmed depth.",
            "   4.2. Verify hanger is set (weight indication).",
            "   4.3. Test liner lap (pressure test).",
            "",
            "5. CEMENT LINER",
            "   5.1. Pump cement per cement program.",
            "   5.2. Displace cement and bump plug.",
            "   5.3. WOC per program.",
            "",
            "6. RELEASE RUNNING TOOL",
            "   6.1. Release liner running tool.",
            "   6.2. Pick up and verify release.",
            "   6.3. POOH above liner top.",
            "   6.4. Circulate clean above liner.",
        ]

        return steps

    # ========================================================================
    # CEMENTING PROCEDURE
    # ========================================================================

    def generate_cementing_procedure(self, casing: object) -> List[str]:
        # Find matching cement design
        cement = None
        for c in self.project.cement_design:
            if c.section_name.lower() == casing.section_name.lower():
                cement = c
                break

        lead_density = f"{cement.lead_slurry_density}" if cement else "TBD"
        tail_density = f"{cement.tail_slurry_density}" if cement else "TBD"
        lead_type = cement.lead_slurry_type if cement else "Class G"
        tail_type = cement.tail_slurry_type if cement else "Class G"
        spacer_type = cement.spacer_type if cement else "Chemical Wash"
        spacer_vol = f"{cement.spacer_volume}" if cement else "TBD"
        disp_vol = f"{cement.displacement_volume}" if cement else "TBD"
        disp_rate = f"{cement.displacement_rate}" if cement else "TBD"
        woc = f"{cement.woc_time}" if cement else "TBD"
        bump_psi = f"{cement.plug_bump_pressure}" if cement else "TBD"

        steps = [
            f"CEMENTING PROCEDURE - {casing.casing_od}\" "
            f"{casing.section_name.upper()} CASING",
            f"Shoe Depth: {casing.setting_depth_md:,.0f} ft MD",
            f"TOC: {casing.top_of_cement_md:,.0f} ft MD",
            "",
            "1. PRE-CEMENT PREPARATION",
            "   1.1. Conduct pre-cement safety meeting.",
            "   1.2. Verify cement program with cement engineer.",
            "   1.3. Verify cement unit is rigged up and tested.",
            "   1.4. Pressure test cement lines to 80% of "
            "expected max pressure.",
            "   1.5. Verify cement products on location:",
            f"        a) Lead slurry: {lead_type} @ {lead_density} ppg",
            f"        b) Tail slurry: {tail_type} @ {tail_density} ppg",
            f"        c) Spacer: {spacer_type}",
            "        d) Wash fluid",
            "        e) All additives per design",
            "   1.6. Verify batch mixer and densitometer calibrated.",
            "   1.7. Establish circulation and record pressures.",
            "   1.8. Verify casing movement (reciprocation/rotation) "
            "if planned.",
            "   1.9. Collect mud sample for compatibility test.",
            "   1.10. Verify ECD calculations will not exceed "
            "fracture gradient.",
            "",
            "2. CONDITIONING",
            "   2.1. Circulate hole clean - minimum 2 x annular volume.",
            "   2.2. Condition mud to target properties:",
            "        a) Reduce rheology to minimum for cement placement",
            "        b) Verify fluid loss properties",
            "   2.3. Record final circulating pressure at "
            "planned pump rate.",
            "   2.4. Record slow pump rates (Kill Rate).",
            "   2.5. Begin reciprocating casing if planned.",
            "",
            "3. PUMPING CEMENT",
            "   3.1. Drop bottom wiper plug.",
            "   3.2. Pump spacer/wash ahead of cement:",
            f"        - Type: {spacer_type}",
            f"        - Volume: {spacer_vol} bbl",
            "   3.3. Pump lead slurry:",
            f"        - Type: {lead_type}",
            f"        - Density: {lead_density} ppg",
            "        - Monitor density at manifold",
            "        - Maintain density within ±0.2 ppg",
            "   3.4. Pump tail slurry:",
            f"        - Type: {tail_type}",
            f"        - Density: {tail_density} ppg",
            "        - Monitor density at manifold",
            "   3.5. Drop top wiper plug.",
            "   3.6. Displace cement:",
            f"        - Displacement volume: {disp_vol} bbl",
            f"        - Displacement rate: {disp_rate} bpm",
            "        - Track displacement volume precisely",
            "   3.7. Monitor:",
            "        a) Surface pressure continuously",
            "        b) ECD (if available from PWD tool)",
            "        c) Returns at flowline",
            "        d) Pit volume changes",
            "   3.8. Slow down displacement rate 5 bbl before "
            "expected plug bump.",
            "",
            "4. PLUG BUMP",
            "   4.1. Observe pressure increase as plug seats.",
            f"   4.2. Bump plug to {bump_psi} psi above "
            "final circulating pressure.",
            "   4.3. Hold pressure for 10 minutes.",
            "   4.4. Bleed off pressure and check for backflow.",
            "   4.5. If plug does not bump:",
            "        a) Continue displacing in small increments",
            "        b) Do not over-displace",
            "        c) Maximum additional volume: 2 bbl",
            "        d) If still no bump, hold pressure and "
            "report to supervisor",
            "",
            "5. WAIT ON CEMENT (WOC)",
            f"   5.1. WOC time: {woc} hours.",
            "   5.2. Monitor casing pressure during WOC.",
            "   5.3. If pressure builds during WOC:",
            "        a) Record pressure build-up rate",
            "        b) Bleed off if exceeds safe limits",
            "        c) Monitor for annular gas migration",
            "   5.4. Do NOT disturb casing during WOC.",
            "",
            "6. POST-CEMENT VERIFICATION",
            "   6.1. After WOC, verify cement has set.",
            "   6.2. Test casing integrity (pressure test "
            "if required).",
            "   6.3. Record all cement job data:",
            "        a) Actual volumes pumped vs planned",
            "        b) Actual pressures vs predicted",
            "        c) Cement returns (if applicable)",
            "        d) Plug bump pressure",
            "        e) Any anomalies during job",
            f"   6.4. {'Schedule CBL/CBIL logging.' if (cement and cement.cbl_cbil_required) else 'CBL/CBIL not required for this section.'}",
            "   6.5. Prepare cement evaluation report.",
        ]

        return steps

    # ========================================================================
    # BOP NIPPLE UP PROCEDURE
    # ========================================================================

    def generate_bop_nipple_up_procedure(self) -> List[str]:
        bop = self.project.bop_stack

        steps = [
            "BOP NIPPLE UP PROCEDURE",
            "",
            "1. PREPARATION",
            f"   1.1. Verify BOP stack components ({bop.bop_type}):",
            f"        - Working Pressure: {bop.working_pressure:,.0f} psi",
            f"        - Bore Size: {bop.bore_size}\"",
            f"        - Manufacturer: {bop.manufacturer}",
            f"   1.2. Verify BOP rams are correct size "
            f"({bop.pipe_ram_size}).",
            "   1.3. Inspect all BOP flanges, studs, and ring gaskets.",
            "   1.4. Verify kill and choke lines.",
            "   1.5. Verify accumulator unit.",
            "",
            "2. INSTALLATION SEQUENCE",
            "   2.1. Install casing head / spool.",
            "   2.2. Install BOP stack in correct sequence "
            "(bottom to top):",
            f"        a) {'Pipe rams (bottom)' if bop.bop_type != 'Annular Preventer' else 'Annular preventer'}",
        ]

        if bop.blind_ram:
            steps.append("        b) Blind/Shear rams")
        if bop.shear_ram:
            steps.append("        c) Shear rams")
        if bop.variable_bore_ram:
            steps.append("        d) Variable bore rams")

        steps.extend([
            "        e) Annular preventer (top)",
            "   2.3. Install kill line and choke line.",
            "   2.4. Install choke manifold.",
            "   2.5. Connect accumulator system.",
            "   2.6. Verify all connections are properly torqued.",
            "",
            "3. FUNCTION TESTING",
            "   3.1. Function test each ram (open and close).",
            "   3.2. Function test annular preventer.",
            "   3.3. Verify remote panel operations.",
            "   3.4. Test all valves on kill/choke lines.",
            "   3.5. Verify accumulator precharge pressure.",
            "   3.6. Record function times for each component.",
            "",
            "4. PRESSURE TESTING",
            f"   4.1. Low pressure test: {bop.bop_test_pressure_low} psi "
            f"for 5 minutes.",
            f"   4.2. High pressure test: "
            f"{bop.bop_test_pressure_high:,.0f} psi for 10 minutes.",
            "   4.3. Acceptable leak rate: 0 psi in 10 minutes.",
            "   4.4. Test each component individually:",
            "        a) Each set of pipe rams",
            "        b) Blind/Shear rams",
            "        c) Annular preventer",
            "        d) Kill line check valve",
            "        e) Choke manifold valves",
            "   4.5. Record all test results.",
            "   4.6. If any test fails, repair and retest.",
            "",
            "5. DOCUMENTATION",
            "   5.1. Complete BOP test report form.",
            "   5.2. Record serial numbers of all components.",
            "   5.3. Note any observations or concerns.",
            "   5.4. Submit test report for approval.",
        ])

        return steps

    # ========================================================================
    # BOP TEST PROCEDURE
    # ========================================================================

    def generate_bop_test_procedure(self) -> List[str]:
        bop = self.project.bop_stack

        steps = [
            "BOP PRESSURE TEST PROCEDURE",
            f"(Per API RP 53 / Company Standards)",
            "",
            "1. TEST FREQUENCY",
            f"   - Function Test: {bop.function_test_frequency}",
            f"   - Pressure Test: {bop.pressure_test_frequency}",
            "   - After initial nipple-up",
            "   - Before drilling out under new casing shoe",
            "   - After any BOP repair or ram change",
            "   - After disconnection of any pressure-containing component",
            "",
            "2. TEST PARAMETERS",
            f"   Low Pressure Test: {bop.bop_test_pressure_low} psi "
            f"for 5 minutes",
            f"   High Pressure Test: {bop.bop_test_pressure_high:,.0f} psi "
            f"for 10 minutes",
            "   Acceptable: No visible leak, no pressure decline",
            "",
            "3. TEST SEQUENCE",
            "   3.1. Notify all personnel of BOP test.",
            "   3.2. Clear non-essential personnel from BOP area.",
            "   3.3. Test sequence (low then high pressure):",
            "",
            "   A. PIPE RAMS TEST",
            "   3.4. Install test plug below rams or "
            "strip in test mandrel.",
            "   3.5. Close pipe rams on drill pipe/test mandrel.",
            f"   3.6. Apply {bop.bop_test_pressure_low} psi - "
            f"hold 5 min.",
            f"   3.7. Increase to {bop.bop_test_pressure_high:,.0f} psi "
            f"- hold 10 min.",
            "   3.8. Record pressures and open rams.",
            "",
            "   B. BLIND/SHEAR RAMS TEST",
            "   3.9. Remove drill pipe from stack.",
            "   3.10. Close blind/shear rams.",
            f"   3.11. Apply {bop.bop_test_pressure_low} psi - "
            f"hold 5 min.",
            f"   3.12. Increase to {bop.bop_test_pressure_high:,.0f} psi "
            f"- hold 10 min.",
            "   3.13. Record and open.",
            "",
            "   C. ANNULAR PREVENTER TEST",
            "   3.14. RIH drill pipe into stack.",
            "   3.15. Close annular on drill pipe.",
            f"   3.16. Apply {bop.bop_test_pressure_low} psi - "
            f"hold 5 min.",
            "   3.17. Apply 70% of annular WP - hold 10 min.",
            "   3.18. Record and open.",
            "",
            "   D. KILL/CHOKE LINE TEST",
            "   3.19. Test kill line valves.",
            "   3.20. Test choke line and choke manifold.",
            "   3.21. Test standpipe manifold valves.",
            "",
            "4. DOCUMENTATION",
            "   4.1. Complete BOP test report.",
            "   4.2. Record all pressures, times, and results.",
            "   4.3. Report any failures and corrective actions.",
            "   4.4. Obtain supervisor sign-off.",
        ]

        return steps

    # ========================================================================
    # LOT / FIT PROCEDURE
    # ========================================================================

    def generate_lot_fit_procedure(self) -> List[str]:
        steps = [
            "LEAK-OFF TEST (LOT) / FORMATION INTEGRITY TEST (FIT) PROCEDURE",
            "",
            "1. PURPOSE",
            "   - Determine formation fracture strength at casing shoe",
            "   - Verify casing cement integrity",
            "   - Confirm wellbore can withstand planned mud weights",
            "   - Calculate MAASP for well control purposes",
            "",
            "2. PREPARATION",
            "   2.1. Drill out cement, shoe track, and float equipment.",
            "   2.2. Drill 10-20 ft of new formation below shoe.",
            "   2.3. Pull back into casing shoe.",
            "   2.4. Circulate clean bottoms up.",
            "   2.5. Stop pumps and observe well for flow (10 min).",
            "   2.6. Verify well is static (no flow).",
            "   2.7. Close annular preventer or pipe rams.",
            "   2.8. Record current mud weight.",
            "",
            "3. LOT / FIT PROCEDURE",
            "   3.1. Prepare cement unit or dedicated test pump.",
            "   3.2. Connect test pump to drill pipe.",
            "   3.3. For LOT (Leak-Off Test):",
            "        a) Pump at constant rate (0.25-0.5 bbl/min)",
            "        b) Record pressure vs volume continuously",
            "        c) Plot pressure vs volume in real-time",
            "        d) Continue until leak-off point observed",
            "        e) Leak-off point = deviation from linear trend",
            "        f) STOP pumping immediately at leak-off",
            "   3.4. For FIT (Formation Integrity Test):",
            "        a) Pump at constant rate (0.25-0.5 bbl/min)",
            "        b) Pump to predetermined pressure equivalent",
            "        c) Hold for 10 minutes",
            "        d) Acceptable: <10% pressure decline",
            "   3.5. Record LOT/FIT pressure.",
            "   3.6. Bleed off pressure slowly.",
            "   3.7. Open BOP.",
            "",
            "4. CALCULATIONS",
            "   4.1. Calculate LOT/FIT equivalent mud weight (EMW):",
            "        EMW = MW + (LOT Pressure / (0.052 × Shoe TVD))",
            "   4.2. Calculate MAASP:",
            "        MAASP = (EMW - Current MW) × 0.052 × Shoe TVD",
            "   4.3. Verify EMW meets minimum design requirements.",
            "",
            "5. REPORTING",
            "   5.1. Report results to office immediately.",
            "   5.2. Record on daily report.",
            "   5.3. Update well control sheet with new MAASP.",
            "   5.4. Obtain approval to continue drilling.",
            "   5.5. If LOT/FIT result is below required value:",
            "        a) Report to office",
            "        b) Consider remedial squeeze cementing",
            "        c) Revise mud weight program if necessary",
        ]

        return steps

    # ========================================================================
    # WELL CONTROL PROCEDURE
    # ========================================================================

    def generate_well_control_procedure(self) -> List[str]:
        wc = self.project.well_control

        steps = [
            "WELL CONTROL PROCEDURE",
            "",
            "1. WELL CONTROL PHILOSOPHY",
            "   - Primary barrier: Hydrostatic pressure (mud weight)",
            "   - Secondary barrier: BOP system",
            "   - Kill method: " + wc.kill_method,
            f"   - Maximum pit gain before shut-in: "
            f"{wc.pit_gain_action_level} bbl",
            "",
            "2. KICK DETECTION INDICATORS",
            "   Primary indicators:",
            "   - Increase in pit volume (pit gain)",
            "   - Increase in return flow rate",
            "   - Well flowing with pumps off",
            "",
            "   Secondary indicators:",
            "   - Drilling break (sudden increase in ROP)",
            "   - Decrease in pump pressure / increase in pump speed",
            "   - Change in hook load (pipe light)",
            "   - Gas cut mud / increase in gas units",
            "   - Increase in connection gas",
            "   - Chloride changes in mud returns",
            "",
            "3. SHUT-IN PROCEDURE (HARD SHUT-IN)",
            "   3.1. DRILLER: Upon positive kick indication:",
            "        a) Pick up off bottom to tool joint above rotary",
            "        b) Stop pumps",
            "        c) Close HCR valve on choke line",
            "        d) Open remote choke line valve",
            "   3.2. DRILLER: Observe and confirm well is flowing.",
            "   3.3. DRILLER: Close pipe rams (preferred) or annular.",
            "   3.4. DRILLER: Notify Toolpusher and Company Man.",
            "   3.5. DRILLER: Record time of shut-in.",
            "   3.6. DRILLER: Allow pressures to stabilize (max 10 min).",
            "   3.7. DRILLER: Record stabilized SIDPP and SICP.",
            "   3.8. DRILLER: Record pit gain.",
            "",
            "4. SHUT-IN PROCEDURE WHILE TRIPPING",
            "   4.1. Set slips and install full opening safety valve.",
            "   4.2. Close full opening safety valve.",
            "   4.3. Close HCR valve.",
            "   4.4. Open remote choke line valve.",
            "   4.5. Close pipe rams.",
            "   4.6. Open safety valve.",
            "   4.7. Record SIDPP and SICP.",
            "   4.8. Calculate kill weight mud.",
            "   4.9. Strip back to bottom if possible.",
            "",
            "5. KILL PROCEDURE - DRILLER'S METHOD",
            "",
            "   First Circulation (circulate kick out):",
            "   5.1. Calculate Initial Circulating Pressure (ICP):",
            f"        ICP = SIDPP + Slow Pump Pressure",
            f"        Slow Pump Rate: {wc.slow_pump_rate_1} SPM, "
            f"Pressure: {wc.slow_pump_pressure_1} psi",
            "   5.2. Slowly open choke and bring pump to kill speed.",
            "   5.3. Maintain drill pipe pressure constant at ICP.",
            "   5.4. Adjust choke to maintain SIDPP.",
            "   5.5. Circulate out kick fluid.",
            "   5.6. When kick is out, shut-in and verify pressures.",
            "",
            "   Second Circulation (circulate kill mud):",
            "   5.7. Calculate kill mud weight:",
            "        Kill MW = Current MW + SIDPP / (0.052 × TVD)",
            "   5.8. Prepare kill weight mud.",
            "   5.9. Begin circulating kill mud:",
            "        - Maintain drill pipe pressure per schedule",
            "        - Start at ICP, reduce linearly to FCP",
            "   5.10. When kill mud reaches bit, maintain "
            "Final Circulating Pressure (FCP).",
            "   5.11. Continue circulating until kill mud returns "
            "at surface.",
            "   5.12. Shut-in and verify SIDPP = 0 and SICP = 0.",
            "   5.13. If both zero, open BOPs and verify well is dead.",
            "",
            "6. KILL PROCEDURE - WAIT & WEIGHT METHOD",
            "   6.1. Record SIDPP and SICP.",
            "   6.2. Calculate kill mud weight.",
            "   6.3. Prepare kill mud weight in pits.",
            "   6.4. Calculate ICP and FCP.",
            "   6.5. Prepare kill sheet (pressure schedule).",
            "   6.6. Begin circulating kill mud:",
            "        - Start at ICP",
            "        - Reduce drill pipe pressure linearly "
            "to FCP as kill mud fills drill string",
            "        - Hold FCP constant once kill mud "
            "reaches bit",
            "   6.7. Continue until kill mud returns.",
            "   6.8. Shut-in and verify dead well.",
            "",
            "7. POST-KILL OPERATIONS",
            "   7.1. Add trip margin (0.2-0.5 ppg above kill MW).",
            "   7.2. Circulate and condition mud.",
            "   7.3. Consider increasing MW if pore pressure "
            "is increasing.",
            "   7.4. Record all events on daily report.",
            "   7.5. Prepare detailed well control report.",
            "   7.6. Conduct post-kill crew debriefing.",
            "",
            "8. SPECIAL SCENARIOS",
            "",
            "   A. UNDERGROUND BLOWOUT",
            "   8.1. If kick cannot be controlled at surface.",
            "   8.2. Monitor casing pressure.",
            "   8.3. Consider bullheading if applicable.",
            "",
            "   B. STRIPPING OPERATIONS",
            "   8.4. If kick taken while tripping.",
            "   8.5. Strip back to bottom through annular.",
            "   8.6. Monitor pit volumes.",
            "   8.7. Lubricate and bleed if necessary.",
            "",
            "   C. GAS IN RISER (Offshore)",
            "   8.8. If gas enters riser.",
            "   8.9. Implement gas handling procedures.",
            "   8.10. Consider diverting if shallow gas.",
        ]

        return steps

    # ========================================================================
    # KICK DRILL PROCEDURE
    # ========================================================================

    def generate_kick_drill_procedure(self) -> List[str]:
        steps = [
            "WELL CONTROL DRILL PROCEDURE",
            "",
            "1. PURPOSE",
            "   - Practice well control procedures with all crews",
            "   - Verify equipment functionality",
            "   - Measure response times",
            "   - Identify and correct deficiencies",
            "",
            "2. FREQUENCY",
            "   - Before spud",
            "   - After crew change",
            "   - Weekly (or as per company policy)",
            "   - After any well control event",
            "",
            "3. DRILL SCENARIOS",
            "   3.1. SCENARIO A: Kick While Drilling",
            "        - Simulate pit gain of 10 bbl",
            "        - Practice hard shut-in procedure",
            "        - Time from first indication to shut-in",
            "        - Target: < 2 minutes",
            "",
            "   3.2. SCENARIO B: Kick While Tripping",
            "        - Simulate flow while pulling out",
            "        - Practice installing safety valve",
            "        - Practice shut-in while tripping",
            "        - Target: < 4 minutes",
            "",
            "   3.3. SCENARIO C: Kick While Making Connection",
            "        - Simulate pit gain on connection",
            "        - Practice shut-in on connection",
            "",
            "   3.4. SCENARIO D: Equipment Failure",
            "        - Simulate choke failure",
            "        - Practice backup procedures",
            "",
            "4. EVALUATION",
            "   4.1. Record all response times.",
            "   4.2. Evaluate crew communication.",
            "   4.3. Identify any equipment issues.",
            "   4.4. Document lessons learned.",
            "   4.5. Sign-off by Toolpusher and Company Man.",
        ]

        return steps

    # ========================================================================
    # STUCK PIPE PROCEDURE
    # ========================================================================

    def generate_stuck_pipe_procedure(self) -> List[str]:
        steps = [
            "STUCK PIPE PREVENTION AND REMEDIATION PROCEDURE",
            "",
            "1. PREVENTION MEASURES",
            "   1.1. Maintain proper mud properties at all times.",
            "   1.2. Keep hole clean - maintain adequate annular velocity.",
            "   1.3. Minimize static time in open hole.",
            "   1.4. Rotate and reciprocate pipe when possible.",
            "   1.5. Minimize differential pressure across permeable zones.",
            "   1.6. Use proper trip practices (keep hole full).",
            "   1.7. Monitor drag trends.",
            "   1.8. Address tight holes promptly.",
            "",
            "2. STUCK PIPE INDICATORS",
            "   - Increasing overpull on connections",
            "   - Increasing torque trend",
            "   - Inability to rotate or reciprocate",
            "   - Sudden increase in drag",
            "   - Pack-off (no circulation)",
            "",
            "3. IMMEDIATE ACTIONS WHEN STUCK",
            "   3.1. DO NOT pull excessively (respect overpull limit).",
            "   3.2. Attempt to circulate.",
            "   3.3. If circulation possible:",
            "        a) Work pipe (rotate and reciprocate)",
            "        b) Increase flow rate if possible",
            "        c) Consider spotting pill",
            "   3.4. If NO circulation:",
            "        a) Apply maximum allowable overpull (jar up)",
            "        b) Apply maximum allowable setdown (jar down)",
            "        c) Attempt to rotate",
            "",
            "4. DETERMINE STICKING MECHANISM",
            "   4.1. Differential sticking:",
            "        - Can circulate but cannot move pipe",
            "        - Usually in permeable formation",
            "        - Actions: Spot oil-based or acid pill",
            "   4.2. Mechanical sticking:",
            "        - Cannot circulate or move pipe",
            "        - Key-seating, undergauge hole, junk",
            "        - Actions: Work pipe, increase MW if needed",
            "   4.3. Pack-off / Bridge:",
            "        - Gradual loss of circulation",
            "        - Cuttings or cavings packing off",
            "        - Actions: Clean hole, increase mud weight",
            "",
            "5. FREEING PROCEDURES",
            "",
            "   A. DIFFERENTIAL STICKING",
            "   5.1. Reduce hydrostatic if safe to do so.",
            "   5.2. Spot diesel/mineral oil pill across stuck zone.",
            "   5.3. Allow soak time (4-8 hours).",
            "   5.4. Work pipe periodically.",
            "   5.5. If unsuccessful, consider acid pill.",
            "",
            "   B. MECHANICAL STICKING",
            "   5.6. Jar up and down within limits.",
            "   5.7. Apply torque and work pipe.",
            "   5.8. If BHA has jar, activate jarring sequence.",
            "   5.9. If unsuccessful after 8-12 hours, "
            "consider backoff.",
            "",
            "6. BACKOFF AND FISHING",
            "   6.1. If pipe cannot be freed after all attempts:",
            "        a) Calculate free point",
            "        b) Run free point indicator",
            "        c) Back off above stuck point",
            "        d) Recover free pipe",
            "        e) Plan fishing operations",
            "   6.2. Maximum fishing time: Per company policy "
            "(typically 72-96 hours).",
            "",
            "7. DOCUMENTATION",
            "   7.1. Record exact time pipe became stuck.",
            "   7.2. Record all parameters at time of sticking.",
            "   7.3. Document all freeing attempts and results.",
            "   7.4. Calculate NPT costs.",
        ]

        return steps

    # ========================================================================
    # LOST CIRCULATION PROCEDURE
    # ========================================================================

    def generate_lost_circulation_procedure(self) -> List[str]:
        steps = [
            "LOST CIRCULATION PREVENTION AND TREATMENT PROCEDURE",
            "",
            "1. PREVENTION",
            "   1.1. Maintain ECD below fracture gradient at all times.",
            "   1.2. Control ROP in known loss zones.",
            "   1.3. Avoid excessive surge pressures when tripping.",
            "   1.4. Monitor ECD continuously with PWD tool.",
            "   1.5. Maintain proper hole cleaning.",
            "   1.6. Pre-treat mud with fine LCM before entering "
            "loss zones.",
            "",
            "2. SEVERITY CLASSIFICATION",
            "   - Seepage Loss: < 10 bbl/hr",
            "   - Partial Loss: 10-50 bbl/hr",
            "   - Severe Loss: 50-100 bbl/hr",
            "   - Total Loss: > 100 bbl/hr or complete loss of returns",
            "",
            "3. SEEPAGE LOSS (< 10 bbl/hr)",
            "   3.1. Increase LCM concentration in active system.",
            "   3.2. LCM Recipe (per 100 bbl):",
            "        - Fine Nut Plug: 5-10 ppb",
            "        - Medium Nut Plug: 5-10 ppb",
            "        - Fine/Medium Mica: 5-10 ppb",
            "        - Cellophane Flakes: 3-5 ppb",
            "   3.3. Continue drilling with LCM in system.",
            "   3.4. Monitor loss rate.",
            "",
            "4. PARTIAL LOSS (10-50 bbl/hr)",
            "   4.1. Reduce pump rate to minimum for hole cleaning.",
            "   4.2. Prepare and spot LCM pill:",
            "        - Volume: 50-100 bbl",
            "        - Fine Nut Plug: 15-20 ppb",
            "        - Medium Nut Plug: 10-15 ppb",
            "        - Coarse Nut Plug: 5-10 ppb",
            "        - Medium/Coarse Mica: 10-15 ppb",
            "        - Cellophane Flakes: 5-10 ppb",
            "   4.3. Spot pill across loss zone.",
            "   4.4. Pull above loss zone.",
            "   4.5. Allow 2-4 hours for pill to set.",
            "   4.6. Attempt circulation.",
            "   4.7. If losses continue, repeat with higher "
            "concentration.",
            "",
            "5. SEVERE LOSS (50-100 bbl/hr)",
            "   5.1. Stop drilling - pull above loss zone.",
            "   5.2. Monitor well for flow.",
            "   5.3. Prepare concentrated LCM pill:",
            "        - Include large particle sizes",
            "        - Consider crosslinked polymer pill",
            "   5.4. Spot pill across loss zone under pressure.",
            "   5.5. If unsuccessful, consider:",
            "        a) Gunk squeeze (diesel-cement-bentonite)",
            "        b) Cement squeeze",
            "        c) Settable pill systems",
            "",
            "6. TOTAL LOSS (Complete Loss of Returns)",
            "   6.1. Stop pumping immediately.",
            "   6.2. Monitor well for flow (well control priority).",
            "   6.3. Keep hole full with water / low density fluid.",
            "   6.4. If well is flowing with losses, this is an "
            "underground blowout risk.",
            "   6.5. Prepare large volume cement plug.",
            "   6.6. Consider:",
            "        a) Blind drilling (if safe)",
            "        b) Cement plug with WOC",
            "        c) Casing shoe pullback",
            "        d) Setting intermediate casing string",
            "",
            "7. CEMENT SQUEEZE FOR LOST CIRCULATION",
            "   7.1. Position drill pipe at top of loss zone.",
            "   7.2. Pump cement slurry across loss zone.",
            "   7.3. Apply squeeze pressure (avoid fracturing).",
            "   7.4. WOC minimum 8-12 hours.",
            "   7.5. Drill out cement and test integrity.",
            "",
            "8. DOCUMENTATION",
            "   8.1. Record depth and rate of losses.",
            "   8.2. Document all treatments and results.",
            "   8.3. Record total volume of fluid lost.",
            "   8.4. Update real-time drilling report.",
        ]

        return steps

    # ========================================================================
    # FISHING PROCEDURE
    # ========================================================================

    def generate_fishing_procedure(self) -> List[str]:
        steps = [
            "FISHING OPERATION PROCEDURE",
            "",
            "1. DECISION TO FISH",
            "   1.1. Evaluate cost of fish vs sidetrack.",
            "   1.2. Consider:",
            "        - Depth and accessibility of fish",
            "        - Type and condition of fish",
            "        - Available fishing tools",
            "        - Estimated fishing time",
            "        - Wellbore condition",
            "        - Impact on well objectives",
            "   1.3. Maximum fishing time: Per company policy.",
            "",
            "2. INFORMATION GATHERING",
            "   2.1. Record fish description:",
            "        a) Fish top depth",
            "        b) Fish bottom depth",
            "        c) Fish OD and ID",
            "        d) Type of connection at top of fish",
            "        e) Condition of fish (stuck, free, damaged)",
            "   2.2. Record hole condition.",
            "   2.3. Calculate free point (stretch test).",
            "",
            "3. FISHING TOOLS",
            "   3.1. Select appropriate tools:",
            "        a) Overshot (for external catch)",
            "        b) Spear (for internal catch)",
            "        c) Taper tap (for internal catch)",
            "        d) Junk basket (for junk recovery)",
            "        e) Magnet (for metal junk)",
            "        f) Milling tools (for clearing obstructions)",
            "   3.2. Verify tool dimensions match fish.",
            "   3.3. Include jar in fishing assembly.",
            "",
            "4. FISHING PROCEDURE",
            "   4.1. Prepare fishing BHA.",
            "   4.2. RIH to top of fish.",
            "   4.3. Circulate and clean area above fish.",
            "   4.4. Engage fish with selected tool.",
            "   4.5. Verify engagement (weight indication).",
            "   4.6. Apply straight pull within safe limits.",
            "   4.7. Jar if required.",
            "   4.8. If unsuccessful, consider:",
            "        a) Washover",
            "        b) Milling",
            "        c) Backoff and re-engage",
            "",
            "5. POST-FISHING",
            "   5.1. POOH with recovered fish.",
            "   5.2. Inspect and record fish condition.",
            "   5.3. Clean hole and resume operations.",
            "   5.4. If fish not recovered, proceed to sidetrack.",
        ]

        return steps

    # ========================================================================
    # H2S EMERGENCY PROCEDURE
    # ========================================================================

    def generate_h2s_procedure(self) -> List[str]:
        steps = [
            "H₂S EMERGENCY RESPONSE PROCEDURE",
            "",
            "1. H₂S HAZARD INFORMATION",
            "   - H₂S is colorless, highly toxic gas",
            "   - Heavier than air (SG = 1.19)",
            "   - Smells like rotten eggs (loses smell at high conc.)",
            "   - Flammable and explosive",
            "",
            "   EXPOSURE LIMITS:",
            "   - 10 ppm: 8-hour TWA (time weighted average)",
            "   - 15 ppm: STEL (short term exposure limit)",
            "   - 20 ppm: Alarm level - don SCBA",
            "   - 100 ppm: Immediately dangerous to life/health (IDLH)",
            "   - 500+ ppm: Can cause death within minutes",
            "",
            "2. PREVENTION / PREPARATION",
            "   2.1. H₂S contingency plan reviewed by all personnel.",
            "   2.2. All personnel H₂S certified.",
            "   2.3. SCBA (Self-Contained Breathing Apparatus) "
            "available at all times.",
            "   2.4. H₂S detectors installed and calibrated.",
            "   2.5. Wind socks installed.",
            "   2.6. Escape routes identified and marked.",
            "   2.7. Safe briefing area established (upwind).",
            "   2.8. Buddy system enforced.",
            "",
            "3. H₂S ALARM LEVELS AND RESPONSE",
            "",
            "   ALERT (10 ppm):",
            "   3.1. Notify all personnel.",
            "   3.2. Ensure SCBA is readily accessible.",
            "   3.3. Check wind direction.",
            "   3.4. Monitor levels closely.",
            "",
            "   ALARM (20 ppm):",
            "   3.5. Sound general alarm.",
            "   3.6. All non-essential personnel evacuate upwind.",
            "   3.7. Essential personnel don SCBA.",
            "   3.8. Attempt to control source.",
            "",
            "   EMERGENCY (50+ ppm):",
            "   3.9. Sound emergency alarm.",
            "   3.10. All personnel evacuate to safe muster point.",
            "   3.11. Account for all personnel.",
            "   3.12. Initiate rescue for any missing/incapacitated.",
            "   3.13. Contact emergency services.",
            "",
            "4. RESCUE PROCEDURE",
            "   4.1. NEVER attempt rescue without SCBA.",
            "   4.2. Approach from upwind direction.",
            "   4.3. Remove victim to fresh air (upwind).",
            "   4.4. Check breathing and pulse.",
            "   4.5. Begin CPR if needed.",
            "   4.6. Administer oxygen.",
            "   4.7. Transport to medical facility.",
            "",
            "5. WELL OPERATIONS DURING H₂S",
            "   5.1. Increase mud weight to kill well if possible.",
            "   5.2. Close in well if necessary.",
            "   5.3. Use zinc-based scavengers in mud system.",
            "   5.4. Monitor all gas returns.",
            "   5.5. Ensure NACE compliant materials in use.",
            "   5.6. Ensure proper flaring/venting of gas.",
        ]

        return steps

    # ========================================================================
    # WELLBORE CLEANUP PROCEDURE
    # ========================================================================

    def generate_wellbore_cleanup_procedure(self) -> List[str]:
        steps = [
            "WELLBORE CLEANUP PROCEDURE",
            "",
            "1. PURPOSE",
            "   - Ensure hole is in condition for casing/logging",
            "   - Remove cuttings, cavings, and debris",
            "   - Condition mud for next operation",
            "",
            "2. PROCEDURE",
            "   2.1. At section TD, circulate minimum 2 x bottoms up.",
            "   2.2. Monitor shaker returns for clean returns.",
            "   2.3. Pump hi-vis sweeps if required:",
            "        - Volume: 30-50 bbl",
            "        - Viscosity: 100+ sec/qt",
            "        - Pump at maximum rate",
            "   2.4. Alternate with low-vis sweeps for turbulent flow.",
            "   2.5. Perform short trip to shoe.",
            "   2.6. Ream through any tight spots.",
            "   2.7. Circulate until shakers show minimal solids.",
            "   2.8. Condition mud for casing run.",
            "   2.9. Reduce gel strengths and rheology.",
            "   2.10. Target properties for casing run:",
            "         - FV: < 50 sec/qt",
            "         - YP: < 15 lb/100ft²",
            "         - Gel 10s: < 8",
            "         - FL: < 5 ml/30min",
        ]

        return steps

    # ========================================================================
    # DIRECTIONAL DRILLING PROCEDURE
    # ========================================================================

    def generate_directional_procedure(self) -> List[str]:
        dp = self.project.directional_plan

        steps = [
            "DIRECTIONAL DRILLING PROCEDURE",
            "",
            "1. DIRECTIONAL PLAN SUMMARY",
            f"   - Survey Tool: {dp.survey_tool}",
            f"   - Kickoff Point: {dp.kickoff_point_md:,.0f} ft MD / "
            f"{dp.kickoff_point_tvd:,.0f} ft TVD",
            f"   - Build Rate: {dp.build_rate}°/100ft",
            f"   - Target Inclination: {dp.target_inclination}°",
            f"   - Target Azimuth: {dp.target_azimuth}°",
            f"   - Maximum DLS: {dp.max_dls}°/100ft",
            f"   - Horizontal Displacement: "
            f"{dp.horizontal_displacement:,.0f} ft",
            "",
            "2. SURVEY PROGRAM",
            f"   2.1. Take surveys every {dp.survey_frequency} ft.",
            "   2.2. Take definitive surveys at casing shoes.",
            "   2.3. Verify survey quality (QC checks):",
            "        a) Total field consistency",
            "        b) Dip angle consistency",
            "        c) Gravity check",
            "   2.4. Cross-reference with offset well surveys.",
            "",
            "3. KICKOFF PROCEDURE",
            f"   3.1. Drill vertical to KOP ({dp.kickoff_point_md:,.0f} ft).",
            "   3.2. Take confirmation survey at KOP.",
            "   3.3. Orient motor to planned azimuth.",
            "   3.4. Begin building angle:",
            f"        - Target build rate: {dp.build_rate}°/100ft",
            "        - Slide to build angle",
            "        - Rotate to clean hole between slides",
            "   3.5. Take surveys after each slide.",
            "   3.6. Verify trajectory vs plan.",
            "",
            "4. BUILD SECTION",
            "   4.1. Continue building angle to target inclination.",
            "   4.2. Monitor DLS - do not exceed maximum.",
            "   4.3. Adjust motor parameters as needed.",
            "   4.4. Monitor for wellbore stability issues.",
            "   4.5. Perform wiper trips as required.",
            "",
            "5. TANGENT / HOLD SECTION",
            "   5.1. Once target inclination reached, hold angle.",
            f"   5.2. Hold inclination: {dp.hold_inclination}°",
            f"   5.3. Hold azimuth: {dp.hold_azimuth}°",
            "   5.4. Use RSS or rotary to maintain trajectory.",
            "   5.5. Monitor for natural walk tendency.",
            "",
            "6. TRAJECTORY MONITORING",
            "   6.1. Plot actual vs planned trajectory regularly.",
            "   6.2. Calculate ellipse of uncertainty.",
            "   6.3. Monitor anti-collision (if nearby wells).",
            "   6.4. Tolerance corridor: ±50 ft (or per plan).",
            "   6.5. If trajectory deviates beyond tolerance:",
            "        a) Stop drilling",
            "        b) Evaluate correction plan",
            "        c) Obtain approval before correcting",
            "",
            "7. ANTI-COLLISION",
            "   7.1. Monitor separation from offset wells.",
            "   7.2. Minimum separation factor: 1.5 (or per plan).",
            "   7.3. Take definitive surveys at critical depths.",
            "   7.4. If separation becomes critical, STOP drilling "
            "and evaluate.",
        ]

        return steps

    # ========================================================================
    # WIRELINE LOGGING PROCEDURE
    # ========================================================================

    def generate_logging_procedure(self) -> List[str]:
        steps = [
            "WIRELINE LOGGING PROCEDURE",
            "",
            "1. PREPARATION",
            "   1.1. Condition hole and mud for logging.",
            "   1.2. Perform wiper trip / short trip to shoe.",
            "   1.3. Circulate bottoms up.",
            "   1.4. POOH drill string.",
            "   1.5. Verify logging unit is rigged up.",
            "   1.6. Calibrate all logging tools.",
            "   1.7. Rig up sheaves and verify wireline path.",
            "   1.8. Conduct pre-job safety meeting.",
            "",
            "2. RUNNING LOGS",
            "   2.1. RIH logging tools to TD.",
            "   2.2. If tools cannot reach TD:",
            "        a) Note depth of obstruction",
            "        b) Log from deepest accessible point",
            "        c) Consider conditioning hole and retry",
            "   2.3. Log from TD upward at specified logging speed.",
            "   2.4. Perform repeat section (200 ft) for QC.",
            "   2.5. Verify log quality in real-time.",
            "   2.6. Record all tool readings and depths.",
            "",
            "3. LOG SUITE (Per Section)",
            "   3.1. Open Hole Logs:",
            "        a) Gamma Ray (GR)",
            "        b) Resistivity (ILD, ILM, SFLU or LWD equiv.)",
            "        c) Neutron Porosity (NPHI)",
            "        d) Density (RHOB)",
            "        e) Sonic (DT)",
            "        f) Caliper",
            "        g) SP (Spontaneous Potential)",
            "   3.2. Special Logs (as required):",
            "        a) FMI / Image Log",
            "        b) MDT / Formation Pressure",
            "        c) CMR / NMR",
            "        d) Dipole Sonic (DSI)",
            "        e) Sidewall Cores",
            "   3.3. Cased Hole Logs:",
            "        a) CBL/VDL (Cement Bond Log)",
            "        b) CBIL (Cement Bond Imaging)",
            "        c) GR-CCL",
            "",
            "4. POST-LOGGING",
            "   4.1. POOH logging tools.",
            "   4.2. Verify all required logs obtained.",
            "   4.3. Review log quality with logging engineer.",
            "   4.4. Transmit data to office.",
            "   4.5. Rig down logging unit.",
            "   4.6. RIH drill string if further operations.",
        ]

        return steps

    # ========================================================================
    # CORING PROCEDURE
    # ========================================================================

    def generate_coring_procedure(self) -> List[str]:
        steps = [
            "CONVENTIONAL CORING PROCEDURE",
            "",
            "1. PREPARATION",
            "   1.1. Verify coring equipment on location.",
            "   1.2. Inspect core barrel, inner barrel, core bit.",
            "   1.3. Prepare core handling equipment.",
            "   1.4. Condition mud for coring:",
            "        - Reduce solids content",
            "        - Optimize filtrate properties",
            "   1.5. Determine coring interval.",
            "   1.6. Conduct pre-job meeting.",
            "",
            "2. CORING OPERATIONS",
            "   2.1. Make up core barrel assembly.",
            "   2.2. RIH to bottom of hole.",
            "   2.3. Tag bottom gently.",
            "   2.4. Begin coring:",
            "        - WOB: 5-15 klbs (lighter than normal)",
            "        - RPM: 40-80 RPM (slower than normal)",
            "        - Flow Rate: Reduced (avoid core washout)",
            "   2.5. Monitor ROP - maintain steady, controlled rate.",
            "   2.6. Maximum single core run: "
            "90 ft (or barrel length).",
            "   2.7. Record all parameters during coring.",
            "   2.8. At end of core run, stop rotation.",
            "   2.9. Apply overpull to break core.",
            "   2.10. POOH slowly and carefully.",
            "",
            "3. CORE HANDLING",
            "   3.1. Lay down core barrel carefully.",
            "   3.2. Extract core from barrel.",
            "   3.3. Mark depth on each core section.",
            "   3.4. Mark 'Top' on each piece.",
            "   3.5. Photograph core at surface.",
            "   3.6. Describe core at wellsite.",
            "   3.7. Preserve cores per laboratory instructions.",
            "   3.8. Ship cores to laboratory promptly.",
            "",
            "4. DOCUMENTATION",
            "   4.1. Record core recovery %.",
            "   4.2. Note any core jamming or loss.",
            "   4.3. Document core description.",
            "   4.4. Complete core analysis request forms.",
        ]

        return steps

    # ========================================================================
    # DST PROCEDURE
    # ========================================================================

    def generate_dst_procedure(self) -> List[str]:
        steps = [
            "DRILL STEM TEST (DST) PROCEDURE",
            "",
            "1. PREPARATION",
            "   1.1. Identify test interval and perforations.",
            "   1.2. Prepare DST string design.",
            "   1.3. Verify surface test equipment.",
            "   1.4. Prepare data acquisition system.",
            "   1.5. Safety meeting - review H₂S plan if applicable.",
            "   1.6. Ensure flare pit / flare boom ready.",
            "   1.7. Verify choke manifold and separator.",
            "",
            "2. DST STRING MAKEUP",
            "   2.1. Packer (retrievable or permanent).",
            "   2.2. Test valve (BPV).",
            "   2.3. Pressure recorders (multiple).",
            "   2.4. Safety joint.",
            "   2.5. Slip joint (if required).",
            "   2.6. Reverse circulating valve.",
            "   2.7. Safety valve at surface.",
            "",
            "3. TESTING PROCEDURE",
            "   3.1. RIH DST string to test depth.",
            "   3.2. Set packer above test interval.",
            "   3.3. Open test valve.",
            "   3.4. Flow Period #1 (Initial Flow): 10-30 min.",
            "   3.5. Shut-in Period #1 (Initial BU): 1-2 hours.",
            "   3.6. Flow Period #2 (Main Flow): 4-24 hours.",
            "   3.7. Shut-in Period #2 (Final BU): 2-4 hours.",
            "   3.8. Record all pressures and rates.",
            "",
            "4. POST-TEST",
            "   4.1. Close test valve.",
            "   4.2. Reverse circulate above packer.",
            "   4.3. Unseat packer.",
            "   4.4. POOH DST string.",
            "   4.5. Download pressure recorder data.",
            "   4.6. Analyze test results.",
            "   4.7. Report results to office.",
        ]

        return steps

    # ========================================================================
    # ABANDONMENT PROCEDURE
    # ========================================================================

    def generate_abandonment_procedure(self) -> List[str]:
        steps = [
            "WELL ABANDONMENT PROCEDURE",
            "(Per Regulatory Requirements)",
            "",
            "1. TEMPORARY ABANDONMENT (P&A)",
            "   1.1. Circulate and condition well.",
            "   1.2. Set cement plug across producing zone:",
            "        a) Minimum 200 ft cement plug",
            "        b) Tag top of cement to verify",
            "   1.3. Test cement plug (apply pressure from above).",
            "   1.4. Set additional cement plugs as required:",
            "        a) Across all hydrocarbon zones",
            "        b) Above and below permeable zones",
            "        c) Inside casing and in annulus",
            "   1.5. Place wellhead cap / tree cap.",
            "   1.6. Document all plug depths and volumes.",
            "",
            "2. PERMANENT ABANDONMENT",
            "   2.1. Follow all regulatory requirements.",
            "   2.2. Set balanced cement plugs across:",
            "        a) All perforated intervals",
            "        b) All open hole sections",
            "        c) At casing shoe depths",
            "        d) Across any aquifer zones",
            "        e) Surface plug (from 200 ft to surface)",
            "   2.3. Cut and recover casing as required.",
            "   2.4. Remove wellhead below ground level.",
            "   2.5. Weld steel plate over well.",
            "   2.6. Restore location to original condition.",
            "   2.7. File abandonment report with authorities.",
        ]

        return steps

    # ========================================================================
    # RIG MOVE PROCEDURE
    # ========================================================================

    def generate_rig_move_procedure(self) -> List[str]:
        steps = [
            "RIG MOVE PROCEDURE",
            "",
            "1. Pre-move inspection and planning",
            "2. Rig down sequence per rig move plan",
            "3. Load and transport equipment",
            "4. Rig up at new location",
            "5. Commissioning and testing",
            "6. Rig acceptance inspection",
        ]
        return steps

    # ========================================================================
    # HSE PROCEDURE
    # ========================================================================

    def generate_hse_procedure(self) -> List[str]:
        steps = [
            "HEALTH, SAFETY & ENVIRONMENT (HSE) PROCEDURE",
            "",
            "1. HSE MANAGEMENT SYSTEM",
            "   1.1. All operations shall comply with company HSE policy.",
            "   1.2. HSE is everyone's responsibility.",
            "   1.3. Stop Work Authority (SWA) applies to all personnel.",
            "   1.4. All incidents shall be reported immediately.",
            "",
            "2. PERSONAL PROTECTIVE EQUIPMENT (PPE)",
            "   Mandatory PPE on rig floor:",
            "   - Hard hat",
            "   - Safety glasses / goggles",
            "   - Steel toe boots",
            "   - Coveralls / FRC (Flame Resistant Clothing)",
            "   - Gloves (appropriate for task)",
            "   - Hearing protection (in designated areas)",
            "",
            "   Additional PPE as required:",
            "   - Fall protection (harness) for work at height",
            "   - SCBA (in H₂S areas)",
            "   - Face shield (for grinding/cutting)",
            "   - Chemical resistant gloves (mud handling)",
            "",
            "3. PERMIT TO WORK SYSTEM",
            "   3.1. Hot Work Permit required for:",
            "        - Welding, cutting, grinding",
            "        - Any ignition source in hazardous area",
            "   3.2. Cold Work Permit required for:",
            "        - Working at height",
            "        - Confined space entry",
            "        - Lifting operations",
            "        - Electrical work",
            "        - Working on pressurized systems",
            "",
            "4. SAFETY MEETINGS",
            "   4.1. Pre-tour (shift) safety meeting - every shift change.",
            "   4.2. Pre-job safety meeting (JSA/TBT) - before "
            "each critical operation.",
            "   4.3. Weekly safety meeting.",
            "   4.4. Monthly HSE review meeting.",
            "",
            "5. ENVIRONMENTAL PROTECTION",
            "   5.1. No discharge to ground or water.",
            "   5.2. All waste segregated and disposed properly.",
            "   5.3. Spill prevention and containment.",
            "   5.4. Air emission monitoring.",
            "   5.5. Noise monitoring and control.",
            "   5.6. Wildlife protection as applicable.",
            "",
            "6. EMERGENCY RESPONSE",
            "   6.1. Emergency Response Plan posted at all locations.",
            "   6.2. Emergency drills scheduled:",
            "        - Fire drill: Monthly",
            "        - Abandon rig drill: Quarterly",
            "        - Well control drill: Weekly",
            "        - H₂S drill: As required",
            "        - Man overboard drill: Monthly (offshore)",
            "   6.3. Emergency equipment inspection: Weekly.",
            "   6.4. First aid equipment inspection: Daily.",
            "",
            "7. INCIDENT REPORTING",
            "   7.1. All incidents reported within 24 hours.",
            "   7.2. Investigation completed within 72 hours.",
            "   7.3. Near-miss reporting encouraged.",
            "   7.4. Lessons learned shared across organization.",
        ]

        return steps

    # ========================================================================
    # HOT WORK PROCEDURE
    # ========================================================================

    def generate_hot_work_procedure(self) -> List[str]:
        steps = [
            "HOT WORK PROCEDURE",
            "",
            "1. Hot Work Permit must be obtained before any hot work.",
            "2. Gas test area before commencing.",
            "3. Fire watch posted during and 30 min after.",
            "4. Fire extinguisher within 10 feet.",
            "5. Combustible materials removed or covered.",
            "6. Continuous gas monitoring during hot work.",
            "7. No hot work within 35m of wellhead without "
            "additional precautions.",
        ]
        return steps

    # ========================================================================
    # CONFINED SPACE PROCEDURE
    # ========================================================================

    def generate_confined_space_procedure(self) -> List[str]:
        steps = [
            "CONFINED SPACE ENTRY PROCEDURE",
            "",
            "1. Obtain Confined Space Entry Permit.",
            "2. Atmospheric testing (O₂, LEL, H₂S, CO).",
            "3. Isolation and lockout/tagout of all energy sources.",
            "4. Continuous monitoring during entry.",
            "5. Standby person at entry point at all times.",
            "6. Rescue plan and equipment in place.",
            "7. Communication maintained with entrant.",
        ]
        return steps

    # ========================================================================
    # HELICOPTER PROCEDURE (OFFSHORE)
    # ========================================================================

    def generate_helicopter_procedure(self) -> List[str]:
        steps = [
            "HELICOPTER OPERATIONS PROCEDURE",
            "",
            "1. Helideck to be inspected before each flight.",
            "2. Fire crew on standby during operations.",
            "3. All passengers briefed on safety procedures.",
            "4. Weight manifest completed.",
            "5. No loose items on helideck.",
            "6. Radio communication maintained.",
            "7. Emergency plan in place.",
        ]
        return steps


# ============================================================================
# MAIN CALCULATION RUNNER
# ============================================================================

class CalculationEngine:
    """موتور اصلی محاسبات"""

    def __init__(self, project):
        self.project = project
        self.hydraulics = HydraulicsCalculator()
        self.torque_drag = TorqueDragCalculator()
        self.cement_calc = CementCalculator()
        self.casing_calc = CasingDesignCalculator()
        self.well_control = WellControlCalculator()
        self.eng = DrillingEngineering()

    def run_all_calculations(self) -> Dict:
        """اجرای تمام محاسبات"""
        results = {}

        # Casing Design Verification
        results['casing'] = self.verify_casing_design()

        # Hydraulics per section
        results['hydraulics'] = self.calculate_all_hydraulics()

        # Cement volumes
        results['cement'] = self.calculate_all_cement()

        # Well Control
        results['well_control'] = self.calculate_well_control()

        return results

    def verify_casing_design(self) -> List[Dict]:
        """تأیید طراحی لوله‌ها"""
        results = []
        for cd in self.project.casing_design:
            if cd.casing_od <= 0:
                continue

            # Get grade yield strength (simplified lookup)
            grade_yield = self._get_grade_yield(cd.casing_grade)

            result = self.casing_calc.calculate_casing_design_summary(
                od=cd.casing_od,
                id_inner=cd.casing_id,
                weight_ppf=cd.casing_weight,
                grade_yield_psi=grade_yield,
                setting_depth_tvd=cd.setting_depth_tvd,
                mud_weight=self._get_mud_weight_for_section(cd.section_name),
                pore_pressure=self._get_max_pore_pressure(cd.setting_depth_tvd),
                fracture_gradient=self._get_frac_gradient(cd.setting_depth_tvd)
            )
            result['section'] = cd.section_name
            results.append(result)

        return results

    def calculate_all_hydraulics(self) -> List[Dict]:
        """محاسبه هیدرولیک برای هر سکشن"""
        results = []
        # Simplified - actual implementation would use detailed BHA data
        for mud in self.project.mud_programs:
            if mud.mud_weight_out <= 0:
                continue
            result = {
                'section': mud.section_name,
                'mud_weight': mud.mud_weight_out,
                'ecd_shoe': mud.ecd_at_shoe,
                'ecd_td': mud.ecd_at_td,
            }
            results.append(result)
        return results

    def calculate_all_cement(self) -> List[Dict]:
        """محاسبه سیمان برای هر سکشن"""
        results = []
        for i, cd in enumerate(self.project.casing_design):
            cement = None
            for c in self.project.cement_design:
                if c.section_name.lower() == cd.section_name.lower():
                    cement = c
                    break

            if cement and cd.casing_od > 0:
                result = self.cement_calc.calculate_full_cement_job(
                    hole_size=cd.hole_size,
                    casing_od=cd.casing_od,
                    casing_id=cd.casing_id,
                    shoe_depth_md=cd.setting_depth_md,
                    shoe_depth_tvd=cd.setting_depth_tvd,
                    toc_md=cd.top_of_cement_md,
                    toc_tvd=cd.top_of_cement_md,  # Simplified
                    float_collar_depth=cd.float_collar_depth,
                    lead_density=cement.lead_slurry_density,
                    lead_yield=cement.lead_slurry_yield if cement.lead_slurry_yield > 0 else 1.15,
                    tail_density=cement.tail_slurry_density,
                    tail_yield=cement.tail_slurry_yield if cement.tail_slurry_yield > 0 else 1.15,
                    tail_length=500,  # Default tail length
                    excess_percent=cement.excess_percentage,
                    mud_weight=self._get_mud_weight_for_section(cd.section_name)
                )
                result['section'] = cd.section_name
                results.append(result)

        return results

    def calculate_well_control(self) -> Dict:
        """محاسبات کنترل چاه"""
        results = {}

        # Find deepest casing shoe
        if self.project.casing_design:
            last_shoe = self.project.casing_design[-1]
            frac_grad = self._get_frac_gradient(last_shoe.setting_depth_tvd)
            mud_weight = self._get_mud_weight_for_section(
                last_shoe.section_name)

            maasp = self.well_control.maasp(
                frac_grad, mud_weight, last_shoe.setting_depth_tvd)
            results['maasp'] = round(maasp, 0)

            # Kick tolerance
            kt = self.well_control.kick_tolerance(
                frac_grad, mud_weight, last_shoe.setting_depth_tvd,
                self.project.well_info.total_depth_tvd,
                12.25, 5.0  # Default hole/pipe sizes
            )
            results['kick_tolerance'] = round(kt, 1)

        return results

    def _get_grade_yield(self, grade: str) -> float:
        """بازیابی مقاومت تسلیم بر اساس گرید"""
        grade_map = {
            'H-40': 40000, 'J-55': 55000, 'K-55': 55000,
            'N-80': 80000, 'L-80': 80000, 'C90': 90000,
            'C-95': 95000, 'T-95': 95000, 'P-110': 110000,
            'Q-125': 125000, 'V-150': 150000,
        }
        for key, value in grade_map.items():
            if key in grade:
                return value
        return 80000  # Default

    def _get_mud_weight_for_section(self, section_name: str) -> float:
        """بازیابی وزن گل سکشن"""
        for mud in self.project.mud_programs:
            if mud.section_name.lower() == section_name.lower():
                return mud.mud_weight_out
        return 9.0  # Default

    def _get_max_pore_pressure(self, tvd: float) -> float:
        """بازیابی حداکثر فشار منفذی"""
        max_pp = 8.6
        for ft in self.project.formation_tops:
            if ft.tvd_bottom <= tvd:
                max_pp = max(max_pp, ft.pore_pressure_bottom)
        return max_pp

    def _get_frac_gradient(self, tvd: float) -> float:
        """بازیابی گرادیان شکست"""
        min_fg = 20.0
        for ft in self.project.formation_tops:
            if ft.tvd_top <= tvd <= ft.tvd_bottom:
                return ft.fracture_gradient_top
            if ft.tvd_bottom <= tvd:
                min_fg = min(min_fg, ft.fracture_gradient_bottom)
        return min_fg


# ============================================================================
# END OF PART 2
# ============================================================================