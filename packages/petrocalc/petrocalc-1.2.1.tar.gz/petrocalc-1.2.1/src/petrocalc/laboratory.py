"""
Petroleum engineering laboratory calculations.

This module contains functions for laboratory measurements and calculations including:
- Viscosity measurements (Saybolt, Ubbelohde)
- Wettability measurements (Amott-Harvey, USBM)
- Contact angle and surface tension
- Permeability measurements
- Porosity calculations
- Drilling mud properties
- Core analysis

Reference: Based on "Formulas and Calculations for Petroleum Engineering"
          Chapter 9: Petroleum engineering laboratory formulas and calculations
"""

import math
from typing import Union, Tuple, Optional


# =============================================================================
# VISCOSITY MEASUREMENTS
# =============================================================================

def absolute_viscosity_saybolt(
    kinematic_viscosity: float,
    fluid_density: float
) -> float:
    """
    Calculate absolute viscosity from Saybolt viscosimeter measurements.
    
    Args:
        kinematic_viscosity (float): Kinematic viscosity in centistokes
        fluid_density (float): Measured density of fluid in g/cm³
        
    Returns:
        float: Absolute viscosity in cP
        
    Reference: Chapter 9, Formulas and Calculations for Petroleum Engineering
    """
    v = kinematic_viscosity
    rho = fluid_density
    
    if rho <= 0:
        raise ValueError("Fluid density must be positive")
    
    mu = v * rho
    return mu


def kinematic_viscosity_saybolt(
    discharge_time: float,
    saybolt_constant: float = 0.226
) -> float:
    """
    Calculate kinematic viscosity from Saybolt viscosimeter measurements.
    
    Args:
        discharge_time (float): Discharge time in seconds
        saybolt_constant (float): Saybolt constant, default 0.226
        
    Returns:
        float: Kinematic viscosity in centistokes
    """
    t = discharge_time
    c = saybolt_constant
    
    if t <= 0:
        raise ValueError("Discharge time must be positive")
    
    v = c * t - (195 / t)
    return max(0, v)


def absolute_viscosity_ubbelohde(
    flow_time: float,
    viscometer_constant: float,
    fluid_density: float
) -> float:
    """
    Calculate absolute viscosity from Ubbelohde viscosimeter measurements.
    
    Args:
        flow_time (float): Flow time in seconds
        viscometer_constant (float): Viscometer constant in cSt/s
        fluid_density (float): Fluid density in g/cm³
        
    Returns:
        float: Absolute viscosity in cP
    """
    t = flow_time
    k = viscometer_constant
    rho = fluid_density
    
    if t <= 0 or rho <= 0:
        raise ValueError("Flow time and density must be positive")
    
    kinematic_visc = k * t
    absolute_visc = kinematic_visc * rho
    return absolute_visc


# =============================================================================
# WETTABILITY MEASUREMENTS
# =============================================================================

def amott_harvey_wettability_index(
    spontaneous_imbibition_oil: float,
    forced_displacement_oil: float,
    spontaneous_imbibition_water: float,
    forced_displacement_water: float
) -> float:
    """
    Calculate Amott-Harvey wettability index.
    
    Args:
        spontaneous_imbibition_oil (float): Spontaneous imbibition oil volume in ml
        forced_displacement_oil (float): Forced displacement oil volume in ml
        spontaneous_imbibition_water (float): Spontaneous imbibition water volume in ml
        forced_displacement_water (float): Forced displacement water volume in ml
        
    Returns:
        float: Amott-Harvey wettability index (-1 to +1)
    """
    vsp_o = spontaneous_imbibition_oil
    vfd_o = forced_displacement_oil
    vsp_w = spontaneous_imbibition_water
    vfd_w = forced_displacement_water
    
    # Calculate displacement ratios
    if (vsp_o + vfd_o) == 0:
        ratio_o = 0
    else:
        ratio_o = vsp_o / (vsp_o + vfd_o)
    
    if (vsp_w + vfd_w) == 0:
        ratio_w = 0
    else:
        ratio_w = vsp_w / (vsp_w + vfd_w)
    
    # Amott-Harvey index
    iw = ratio_w - ratio_o
    return iw


def usbm_wettability_index(
    area_water_drive: float,
    area_oil_drive: float
) -> float:
    """
    Calculate USBM (U.S. Bureau of Mines) wettability index.
    
    Args:
        area_water_drive (float): Area under water drive curve
        area_oil_drive (float): Area under oil drive curve
        
    Returns:
        float: USBM wettability index
    """
    a_w = area_water_drive
    a_o = area_oil_drive
    
    if a_o <= 0:
        raise ValueError("Area under oil drive curve must be positive")
    
    iw = math.log10(a_w / a_o)
    return iw


def contact_angle(
    adhesion_tension: float,
    surface_tension: float
) -> float:
    """
    Calculate contact angle from surface tension measurements.
    
    Args:
        adhesion_tension (float): Adhesion tension in dyne/cm
        surface_tension (float): Surface tension in dyne/cm
        
    Returns:
        float: Contact angle in degrees
    """
    at = adhesion_tension
    st = surface_tension
    
    if st <= 0:
        raise ValueError("Surface tension must be positive")
    
    cos_theta = at / st
    
    # Ensure value is within valid range for arccos
    cos_theta = max(-1, min(1, cos_theta))
    
    theta_rad = math.acos(cos_theta)
    theta_deg = math.degrees(theta_rad)
    
    return theta_deg


def adhesion_tension(surface_tension: float, contact_angle: float) -> float:
    """
    Calculate adhesion tension.
    
    Args:
        surface_tension (float): Surface tension in dyne/cm
        contact_angle (float): Contact angle in degrees
        
    Returns:
        float: Adhesion tension in dyne/cm
    """
    st = surface_tension
    theta = math.radians(contact_angle)
    
    at = st * math.cos(theta)
    return at


# =============================================================================
# SURFACE TENSION MEASUREMENTS
# =============================================================================

def facial_tension_de_nouy_ring(
    force_measurement: float,
    correction_factor: float,
    ring_circumference: float
) -> float:
    """
    Calculate facial tension using De Nouy ring method.
    
    Args:
        force_measurement (float): Force measurement in dyne
        correction_factor (float): Correction factor (dimensionless)
        ring_circumference (float): Ring circumference in cm
        
    Returns:
        float: Facial tension in dyne/cm
    """
    f = force_measurement
    cf = correction_factor
    l = ring_circumference
    
    if l <= 0:
        raise ValueError("Ring circumference must be positive")
    
    gamma = (f * cf) / l
    return gamma


def correction_factor_de_nouy_ring(
    ring_radius: float,
    meniscus_height: float,
    density_difference: float
) -> float:
    """
    Calculate correction factor for De Nouy ring method.
    
    Args:
        ring_radius (float): Ring radius in cm
        meniscus_height (float): Meniscus height in cm
        density_difference (float): Density difference between phases in g/cm³
        
    Returns:
        float: Correction factor (dimensionless)
    """
    r = ring_radius
    h = meniscus_height
    drho = density_difference
    
    if r <= 0:
        raise ValueError("Ring radius must be positive")
    
    # Simplified correction factor calculation
    cf = 1.0 + 0.5 * (h / r) + 0.1 * drho
    return cf


# =============================================================================
# PERMEABILITY MEASUREMENTS
# =============================================================================

def liquid_permeability_lab(
    flow_rate: float,
    viscosity: float,
    length: float,
    area: float,
    pressure_drop: float
) -> float:
    """
    Calculate liquid permeability from permeameter lab measurement.
    
    Args:
        flow_rate (float): Flow rate in ml/s
        viscosity (float): Fluid viscosity in cP
        length (float): Core length in cm
        area (float): Cross-sectional area in cm²
        pressure_drop (float): Pressure drop in atm
        
    Returns:
        float: Permeability in md
    """
    q = flow_rate
    mu = viscosity
    l = length
    a = area
    dp = pressure_drop
    
    if a <= 0 or dp <= 0:
        raise ValueError("Area and pressure drop must be positive")
    
    # Darcy's law (converting to md)
    k_darcy = (q * mu * l) / (a * dp)
    k_md = k_darcy * 1013.25  # Convert from darcy to md (atm to bar conversion factor)
    
    return k_md


def gas_permeability_klinkenberg(
    apparent_permeability: float,
    mean_pressure: float,
    klinkenberg_constant: float
) -> float:
    """
    Calculate gas permeability using Klinkenberg effect correction.
    
    Args:
        apparent_permeability (float): Apparent permeability in md
        mean_pressure (float): Mean pressure in atm
        klinkenberg_constant (float): Klinkenberg constant in atm
        
    Returns:
        float: Liquid-equivalent permeability in md
    """
    ka = apparent_permeability
    pm = mean_pressure
    b = klinkenberg_constant
    
    if pm <= 0:
        raise ValueError("Mean pressure must be positive")
    
    k_liquid = ka / (1 + b / pm)
    return k_liquid


def permeability_kozeny_carman_lab(
    porosity: float,
    specific_surface_area: float,
    kozeny_constant: float = 5.0
) -> float:
    """
    Calculate permeability using Kozeny-Carman equation with lab data.
    
    Args:
        porosity (float): Porosity as fraction
        specific_surface_area (float): Specific surface area in cm²/cm³
        kozeny_constant (float): Kozeny constant, default 5.0
        
    Returns:
        float: Permeability in md
    """
    phi = porosity
    s = specific_surface_area
    k0 = kozeny_constant
    
    if phi <= 0 or phi >= 1 or s <= 0:
        raise ValueError("Invalid porosity or specific surface area")
    
    k = (phi**3) / (k0 * (1 - phi)**2 * s**2)
    
    # Convert to md (assuming CGS units)
    k_md = k * 1.013e12  # Conversion factor for CGS to md
    
    return k_md


def relative_permeability_lab(
    effective_permeability: float,
    absolute_permeability: float
) -> float:
    """
    Calculate relative permeability from lab measurements.
    
    Args:
        effective_permeability (float): Effective permeability in md
        absolute_permeability (float): Absolute permeability in md
        
    Returns:
        float: Relative permeability (fraction)
    """
    ke = effective_permeability
    k = absolute_permeability
    
    if k <= 0:
        raise ValueError("Absolute permeability must be positive")
    
    kr = ke / k
    return max(0, min(1, kr))


# =============================================================================
# POROSITY MEASUREMENTS
# =============================================================================

def effective_porosity_lab(
    bulk_volume: float,
    grain_volume: float
) -> float:
    """
    Calculate effective porosity from lab measurements.
    
    Args:
        bulk_volume (float): Bulk volume in cm³
        grain_volume (float): Grain volume in cm³
        
    Returns:
        float: Effective porosity as fraction
    """
    vb = bulk_volume
    vg = grain_volume
    
    if vb <= 0:
        raise ValueError("Bulk volume must be positive")
    
    phi_e = (vb - vg) / vb
    return max(0, min(1, phi_e))


def total_porosity_lab(
    bulk_volume: float,
    solid_volume: float
) -> float:
    """
    Calculate total porosity from lab measurements.
    
    Args:
        bulk_volume (float): Bulk volume in cm³
        solid_volume (float): Solid volume in cm³
        
    Returns:
        float: Total porosity as fraction
    """
    vb = bulk_volume
    vs = solid_volume
    
    if vb <= 0:
        raise ValueError("Bulk volume must be positive")
    
    phi_t = (vb - vs) / vb
    return max(0, min(1, phi_t))


def porosity_error_percentage(
    measured_porosity: float,
    true_porosity: float
) -> float:
    """
    Calculate error percentage of porosity measurements.
    
    Args:
        measured_porosity (float): Measured porosity as fraction
        true_porosity (float): True porosity as fraction
        
    Returns:
        float: Error percentage
    """
    phi_m = measured_porosity
    phi_t = true_porosity
    
    if phi_t == 0:
        raise ValueError("True porosity cannot be zero")
    
    error = ((phi_m - phi_t) / phi_t) * 100
    return error


# =============================================================================
# DRILLING MUD PROPERTIES
# =============================================================================

def drilling_mud_density(
    mud_weight: float,
    solid_content: float
) -> float:
    """
    Calculate drilling mud density from solid content analysis.
    
    Args:
        mud_weight (float): Mud weight in ppg
        solid_content (float): Solid content as fraction
        
    Returns:
        float: Drilling mud density in g/cm³
    """
    mw = mud_weight
    sc = solid_content
    
    # Convert ppg to g/cm³
    density = mw * 0.1198  # Conversion factor
    
    # Adjust for solid content
    adjusted_density = density * (1 + 0.5 * sc)
    
    return adjusted_density


def clay_concentration_methylene_blue(
    methylene_blue_consumption: float,
    sample_weight: float
) -> float:
    """
    Calculate clay concentration using methylene blue test.
    
    Args:
        methylene_blue_consumption (float): Methylene blue consumption in ml
        sample_weight (float): Sample weight in g
        
    Returns:
        float: Clay concentration in meq/100g
    """
    mb = methylene_blue_consumption
    ws = sample_weight
    
    if ws <= 0:
        raise ValueError("Sample weight must be positive")
    
    # Standard methylene blue test calculation
    clay_conc = (mb * 5) / ws  # 5 is the standard factor for meq/100g
    
    return clay_conc


def solid_content_ratio_drilling_mud(
    wet_weight: float,
    dry_weight: float
) -> float:
    """
    Calculate solid content ratio of drilling mud.
    
    Args:
        wet_weight (float): Wet weight of mud sample in g
        dry_weight (float): Dry weight of mud sample in g
        
    Returns:
        float: Solid content ratio as fraction
    """
    ww = wet_weight
    wd = dry_weight
    
    if ww <= 0:
        raise ValueError("Wet weight must be positive")
    
    scr = wd / ww
    return min(1, scr)


def yield_clays_drilling_fluids(
    clay_weight: float,
    water_volume: float,
    viscosity_increase: float
) -> float:
    """
    Calculate yield of clays as drilling fluids.
    
    Args:
        clay_weight (float): Clay weight in g
        water_volume (float): Water volume in ml
        viscosity_increase (float): Viscosity increase in cP
        
    Returns:
        float: Clay yield in bbl/ton
    """
    wc = clay_weight
    vw = water_volume
    dv = viscosity_increase
    
    if wc <= 0:
        raise ValueError("Clay weight must be positive")
    
    # Empirical yield calculation
    yield_value = (vw * dv) / (wc * 42)  # 42 is conversion factor for bbl/ton
    
    return yield_value


# =============================================================================
# SPECIALIZED LABORATORY MEASUREMENTS
# =============================================================================

def resistivity_measurement(resistance: float, geometry_factor: float) -> float:
    """
    Calculate resistivity from resistance measurement.
    
    Args:
        resistance (float): Measured resistance in ohms
        geometry_factor (float): Geometry factor in m
        
    Returns:
        float: Resistivity in ohm·m
    """
    r = resistance
    gf = geometry_factor
    
    resistivity = r * gf
    return resistivity


def resistivity_index_archie_lab(
    saturated_resistivity: float,
    brine_resistivity: float
) -> float:
    """
    Calculate resistivity index using Archie's law from lab data.
    
    Args:
        saturated_resistivity (float): 100% brine saturated resistivity in ohm·m
        brine_resistivity (float): Brine resistivity in ohm·m
        
    Returns:
        float: Resistivity index (dimensionless)
    """
    rt = saturated_resistivity
    rw = brine_resistivity
    
    if rw <= 0:
        raise ValueError("Brine resistivity must be positive")
    
    ri = rt / rw
    return ri


def average_compressibility_oil(
    v_ref: float,
    v1: float,
    v2: float,
    p1: float,
    p2: float
) -> float:
    """
    Calculate average compressibility of oil.
    
    Args:
        v_ref: Reference Volume (volume fraction relative to bubble point)
        v1: Volume Fraction at Higher Pressure (fraction)
        v2: Volume Fraction at Lower Pressure (fraction)
        p1: Pressure Relative to V1 (psi)
        p2: Pressure Relative to V2 (psi)
    
    Returns:
        float: Average Compressibility of Oil (psi^-1)
    
    Reference:
        Craft, B. C., Hawkins, M., & Terry, R. E. (1991). Applied Petroleum 
        Reservoir Engineering. 2nd Edition, Page: 38.
    """
    if p1 == p2:
        raise ValueError("Pressures cannot be equal")
    
    co = -(1 / v_ref) * (v1 - v2) / (p1 - p2)
    return co


def average_gas_solubility(
    s1: float,
    s2: float,
    p1: float,
    p2: float
) -> float:
    """
    Calculate average gas solubility.
    
    Args:
        s1: Solubility at p1 (SCF/STB)
        s2: Solubility at p2 (SCF/STB)
        p1: Pressure1 (psi)
        p2: Pressure2 (psi)
    
    Returns:
        float: Average Gas Solubility (SCF/STB/psi)
    
    Reference:
        Craft, B. C., Hawkins, M., & Terry, R. E. (1991). Applied Petroleum 
        Reservoir Engineering. 2nd Edition, Page: 32.
    """
    if p1 == p2:
        raise ValueError("Pressures cannot be equal")
    
    savg = (s1 - s2) / (p1 - p2)
    return savg


def characterization_factor_oil_distillation(
    tb: float,
    specific_gravity: float
) -> float:
    """
    Calculate characterization factor for oil distillation.
    
    Args:
        tb: Average Boiling Point (°R or °F + 460)
        specific_gravity: Specific Gravity at 60/60°F (dimensionless)
    
    Returns:
        float: Characterization Factor (dimensionless)
    
    Reference:
        Mihcakan, I.M., Alkan, K.H., Ugur, Z., Petroleum and Natural Gas Laboratory,
        Course Notes, I-Fluid Properties, ITU, Petroleum and Natural Gas Engineering,
        Istanbul, Turkey, 2001. Page: 5–2.
    """
    if specific_gravity <= 0:
        raise ValueError("Specific gravity must be positive")
    
    k = tb**(1/3) / specific_gravity
    return k


def clausius_clapeyron_water_vapor(
    lv: float,
    t1: float,
    t2: float,
    r_gas: float,
    pv2: float
) -> float:
    """
    Calculate vapor pressure using Clausius-Clapeyron equation for water vapor.
    
    Args:
        lv: Heat of Vaporization of one mole of Liquid (J/mol)
        t1: Absolute Temperature of Condition 1 (°F)
        t2: Absolute Temperature of Condition 2 (°F)
        r_gas: Gas Constant for Water Vapor (psi/mol·°F·s2)
        pv2: Vapor Pressure at Temperature T2 (psi)
    
    Returns:
        float: Vapor Pressure at Temperature T1 (psi)
    
    Reference:
        McCain Jr, W. D. (1990). Properties of Petroleum Fluids. 
        PennWell Corporation. Page: 54.
    """
    import math
    
    if t1 <= 0 or t2 <= 0:
        raise ValueError("Absolute temperatures must be positive")
    
    ln_ratio = (lv / r_gas) * (1/t1 - 1/t2)
    pv1 = pv2 * math.exp(ln_ratio)
    return pv1


def apparent_facial_tension_de_nouy_ring(
    measured_weight: float,
    ring_perimeter: float,
    gravity: float = 980.0
) -> float:
    """
    Calculate apparent facial tension using De Nouy ring method.
    
    Args:
        measured_weight: Measured Weight (g)
        ring_perimeter: Perimeter of the Ring (cm)
        gravity: Acceleration of Gravity (cm/s²), default = 980.0
    
    Returns:
        float: Apparent Facial Tension (dyn/cm)
    
    Reference:
        Mihcakan, I.M., Alkan, K.H., Ugur, Z., Petroleum and Natural Gas Laboratory,
        Course Notes, I-Fluid Properties, ITU, Petroleum and Natural Gas Engineering,
        Istanbul, Turkey, 2001. Page: 4–3.
    """
    if ring_perimeter <= 0:
        raise ValueError("Ring perimeter must be positive")
    
    s = (measured_weight * gravity) / (2 * ring_perimeter)
    return s


def methylene_blue_test_clay_concentration(
    vmb: float,
    vdm: float,
    vsc: float,
    clay_factor: float = 2.6
) -> dict:
    """
    Calculate clay concentration using methylene blue test.
    
    Args:
        vmb: Volume of Methylene Blue used (mL)
        vdm: Volume of Drilling Mud used (mL)
        vsc: Volume of Solid Content (g)
        clay_factor: Clay factor, default = 2.6
    
    Returns:
        dict: Dictionary containing MBT results and clay concentration
    
    Reference:
        Altun, G., Drilling Fluids Lab, Course Notes, ITU Petroleum and Natural Gas Engineering,
        Istanbul, Turkey, 2013–2014. Experiment 3, Page: 4.
    """
    if vdm <= 0 or vsc <= 0:
        raise ValueError("Volumes must be positive")
    
    mbt_m = vmb / vdm
    mbt_ds = vmb / vsc
    
    # Simplified calculation for clay concentration
    cc = mbt_m * 21.7  # lb/bbl
    
    return {
        'mbt_mud': mbt_m,
        'mbt_solids': mbt_ds,
        'clay_concentration_lb_bbl': cc
    }


def contact_angle_interfacial_tension(
    sigma_so: float,
    sigma_sw: float,
    sigma_wo: float
) -> float:
    """
    Calculate contact angle from interfacial tensions.
    
    Args:
        sigma_so: Interfacial Tension between solid and oil (dyn/cm)
        sigma_sw: Interfacial Tension between solid and water (dyn/cm)
        sigma_wo: Interfacial Tension between water and oil (dyn/cm)
    
    Returns:
        float: Contact Angle (degrees)
    
    Reference:
        Tiab, D., & Donaldson, E. C. (2015). Petrophysics: Theory and Practice of 
        Measuring Reservoir Rock and Fluid Transport Properties. Gulf Professional Publishing. Page: 362.
    """
    import math
    
    if sigma_wo <= 0:
        raise ValueError("Water-oil interfacial tension must be positive")
    
    cos_theta = (sigma_so - sigma_sw) / sigma_wo
    
    # Ensure value is within valid range for arccos
    cos_theta = max(-1, min(1, cos_theta))
    
    theta_rad = math.acos(cos_theta)
    theta_deg = math.degrees(theta_rad)
    
    return theta_deg


def standard_discharge_time_saybolt(
    kinematic_viscosity: float,
    saybolt_constant: float = 0.226
) -> float:
    """
    Calculate standard discharge time for Saybolt viscosimeter.
    
    Args:
        kinematic_viscosity: Kinematic viscosity (centistokes)
        saybolt_constant: Saybolt constant, default = 0.226
    
    Returns:
        float: Standard discharge time (seconds)
    
    Reference:
        Laboratory measurement standards for Saybolt viscosimeter.
    """
    if kinematic_viscosity <= 0:
        raise ValueError("Kinematic viscosity must be positive")
    
    # Solving the Saybolt equation for time: v = c*t - 195/t
    # This gives a quadratic equation: c*t² - v*t - 195 = 0
    a = saybolt_constant
    b = -kinematic_viscosity
    c = -195
    
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        raise ValueError("No real solution exists for given parameters")
    
    import math
    t = (-b + math.sqrt(discriminant)) / (2*a)
    return t


def pycnometer_volume_correction(
    v_nominal: float,
    temp_measurement: float,
    temp_calibration: float = 20.0,
    expansion_coeff: float = 2.1e-4
) -> float:
    """
    Calculate pycnometer volume correction for temperature.
    
    Args:
        v_nominal: Nominal volume at calibration temperature (mL)
        temp_measurement: Measurement temperature (°C)
        temp_calibration: Calibration temperature (°C), default = 20.0
        expansion_coeff: Thermal expansion coefficient (1/°C), default = 2.1e-4
    
    Returns:
        float: Corrected volume (mL)
    
    Reference:
        Standard laboratory practice for pycnometer volume corrections.
    """
    delta_t = temp_measurement - temp_calibration
    v_corrected = v_nominal * (1 + expansion_coeff * delta_t)
    return v_corrected


def relative_centrifugal_force(
    rpm: float,
    radius: float
) -> float:
    """
    Calculate relative centrifugal force.
    
    Args:
        rpm: Rotational speed (revolutions per minute)
        radius: Radius from center of rotation (cm)
    
    Returns:
        float: Relative centrifugal force (dimensionless)
    
    Reference:
        Standard centrifuge calculations for laboratory measurements.
    """
    if rpm <= 0 or radius <= 0:
        raise ValueError("RPM and radius must be positive")
    
    rcf = 1.118e-5 * rpm**2 * radius
    return rcf


def reservoir_wettability_rise_in_core(
    height_oil: float,
    height_water: float,
    contact_angle_oil: float,
    contact_angle_water: float,
    surface_tension_oil: float,
    surface_tension_water: float
) -> float:
    """
    Calculate reservoir wettability using rise in core method.
    
    Args:
        height_oil: Height of oil rise (cm)
        height_water: Height of water rise (cm)
        contact_angle_oil: Contact angle with oil (degrees)
        contact_angle_water: Contact angle with water (degrees)
        surface_tension_oil: Surface tension of oil (dyn/cm)
        surface_tension_water: Surface tension of water (dyn/cm)
    
    Returns:
        float: Wettability index (dimensionless)
    
    Reference:
        Laboratory wettability measurement methods.
    """
    import math
    
    # Convert angles to radians
    theta_o_rad = math.radians(contact_angle_oil)
    theta_w_rad = math.radians(contact_angle_water)
    
    # Calculate wettability index
    numerator = height_oil * surface_tension_oil * math.cos(theta_o_rad)
    denominator = height_water * surface_tension_water * math.cos(theta_w_rad)
    
    if denominator == 0:
        raise ValueError("Water term cannot be zero")
    
    wettability_index = numerator / denominator
    return wettability_index


def resistivity_index_archies_law(
    formation_resistivity: float,
    water_resistivity: float
) -> float:
    """
    Calculate resistivity index using Archie's law.
    
    Args:
        formation_resistivity: Formation resistivity (ohm-m)
        water_resistivity: Formation water resistivity (ohm-m)
    
    Returns:
        float: Resistivity index (dimensionless)
    
    Reference:
        Archie, G.E. (1942). The electrical resistivity log as an aid in 
        determining some reservoir characteristics.
    """
    if water_resistivity <= 0:
        raise ValueError("Water resistivity must be positive")
    
    ri = formation_resistivity / water_resistivity
    return ri


def specific_gravity_air_de_nouy_ring(
    weight_air: float,
    weight_water: float,
    temp: float = 20.0
) -> float:
    """
    Calculate specific gravity of air (upper phase) using De Nouy ring method.
    
    Args:
        weight_air: Weight measured in air (g)
        weight_water: Weight measured in water (g)
        temp: Temperature (°C), default = 20.0
    
    Returns:
        float: Specific gravity of air (dimensionless)
    
    Reference:
        De Nouy ring method for density measurements.
    """
    if weight_water <= 0:
        raise ValueError("Weight in water must be positive")
    
    # Water density at 20°C is approximately 1.0 g/cm³
    water_density = 1.0 - (temp - 20) * 2.1e-4  # Temperature correction
    
    specific_gravity = weight_air / (weight_air - weight_water) * water_density
    return specific_gravity


def filtration_rate_api_fluid_loss(
    volume_filtrate: float,
    time_period: float,
    area: float
) -> float:
    """
    Calculate filtration rate for API fluid loss measurement.
    
    Args:
        volume_filtrate: Volume of filtrate collected (mL)
        time_period: Time period of measurement (minutes)
        area: Filter area (cm²)
    
    Returns:
        float: Filtration rate (mL/min/cm²)
    
    Reference:
        API recommended practice for field testing water-based drilling fluids.
    """
    if time_period <= 0 or area <= 0:
        raise ValueError("Time period and area must be positive")
    
    filtration_rate = volume_filtrate / (time_period * area)
    return filtration_rate


def filtration_volume_without_spurt_loss(
    total_volume: float,
    spurt_loss: float
) -> float:
    """
    Calculate filtration volume without spurt loss.
    
    Args:
        total_volume: Total filtrate volume (mL)
        spurt_loss: Spurt loss volume (mL)
    
    Returns:
        float: Filtration volume without spurt loss (mL)
    
    Reference:
        API fluid loss test procedures.
    """
    if spurt_loss < 0:
        raise ValueError("Spurt loss cannot be negative")
    
    volume_without_spurt = total_volume - spurt_loss
    return max(0, volume_without_spurt)


def filtration_volume_with_spurt_loss(
    measured_volume: float,
    time_ratio: float,
    spurt_loss: float
) -> float:
    """
    Calculate filtration volume with spurt loss correction.
    
    Args:
        measured_volume: Measured filtrate volume (mL)
        time_ratio: Ratio of actual time to standard time (dimensionless)
        spurt_loss: Spurt loss volume (mL)
    
    Returns:
        float: Corrected filtration volume (mL)
    
    Reference:
        API fluid loss test procedures with spurt loss correction.
    """
    if time_ratio <= 0:
        raise ValueError("Time ratio must be positive")
    
    # Correct for time and add spurt loss
    corrected_volume = measured_volume / math.sqrt(time_ratio) + spurt_loss
    return corrected_volume
