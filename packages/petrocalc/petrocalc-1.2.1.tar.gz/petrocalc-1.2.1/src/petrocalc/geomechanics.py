"""
Geomechanics and fracturing calculations.

This module contains functions for geomechanical analysis and hydraulic fracturing including:
- Stress calculations around wellbores
- Rock mechanical properties
- Fracture pressure and gradient calculations
- Formation strength and failure criteria
- Effective stress calculations
- Fracture mechanics

Reference: Based on "Formulas and Calculations for Petroleum Engineering"
          Chapter 11: Geomechanics and fracturing formulas and calculations
"""

import math
from typing import Union, Tuple, Optional


# =============================================================================
# STRESS CALCULATIONS
# =============================================================================

def axial_stress_vertical_wellbore(
    far_field_stress: float,
    pore_pressure: float,
    wellbore_pressure: float,
    wellbore_radius: float,
    radial_distance: float
) -> float:
    """
    Calculate axial stress around vertical wellbore.
    
    Args:
        far_field_stress (float): Far-field axial stress in psi
        pore_pressure (float): Pore pressure in psi
        wellbore_pressure (float): Wellbore pressure in psi
        wellbore_radius (float): Wellbore radius in inches
        radial_distance (float): Radial distance from wellbore center in inches
        
    Returns:
        float: Axial stress in psi
    """
    sigma_z = far_field_stress
    pp = pore_pressure
    pw = wellbore_pressure
    rw = wellbore_radius
    r = radial_distance
    
    if r <= rw:
        raise ValueError("Radial distance must be greater than wellbore radius")
    
    sigma_z_r = sigma_z - (pw - pp) * (rw / r)**2
    return sigma_z_r


def radial_stress_vertical_wellbore(
    horizontal_stress_max: float,
    horizontal_stress_min: float,
    pore_pressure: float,
    wellbore_pressure: float,
    wellbore_radius: float,
    radial_distance: float,
    angle: float = 0.0
) -> float:
    """
    Calculate radial stress around vertical wellbore.
    
    Args:
        horizontal_stress_max (float): Maximum horizontal stress in psi
        horizontal_stress_min (float): Minimum horizontal stress in psi
        pore_pressure (float): Pore pressure in psi
        wellbore_pressure (float): Wellbore pressure in psi
        wellbore_radius (float): Wellbore radius in inches
        radial_distance (float): Radial distance from wellbore center in inches
        angle (float): Angle from maximum horizontal stress direction in degrees
        
    Returns:
        float: Radial stress in psi
    """
    sh_max = horizontal_stress_max
    sh_min = horizontal_stress_min
    pp = pore_pressure
    pw = wellbore_pressure
    rw = wellbore_radius
    r = radial_distance
    theta = math.radians(angle)
    
    if r <= rw:
        raise ValueError("Radial distance must be greater than wellbore radius")
    
    # Simplified radial stress for vertical wellbore
    if r == rw:
        sigma_r = pw
    else:
        sigma_r = ((sh_max + sh_min) / 2) * (1 - (rw / r)**2) + \
                  ((sh_max - sh_min) / 2) * (1 - 4*(rw / r)**2 + 3*(rw / r)**4) * math.cos(2*theta)
    
    return sigma_r


def tangential_stress_wellbore_wall(
    horizontal_stress_max: float,
    horizontal_stress_min: float,
    pore_pressure: float,
    wellbore_pressure: float,
    angle: float = 0.0
) -> float:
    """
    Calculate tangential stress (hoop stress) at wellbore wall.
    
    Args:
        horizontal_stress_max (float): Maximum horizontal stress in psi
        horizontal_stress_min (float): Minimum horizontal stress in psi
        pore_pressure (float): Pore pressure in psi
        wellbore_pressure (float): Wellbore pressure in psi
        angle (float): Angle from maximum horizontal stress direction in degrees
        
    Returns:
        float: Tangential stress in psi
    """
    sh_max = horizontal_stress_max
    sh_min = horizontal_stress_min
    pp = pore_pressure
    pw = wellbore_pressure
    theta = math.radians(angle)
    
    # Tangential stress at wellbore wall
    sigma_theta = (sh_max + sh_min) - 2 * (sh_max - sh_min) * math.cos(2*theta) - pw
    
    return sigma_theta


def effective_stress_individual_grains(
    total_stress: float,
    pore_pressure: float,
    biot_coefficient: float = 1.0
) -> float:
    """
    Calculate effective stress on individual grains.
    
    Args:
        total_stress (float): Total stress in psi
        pore_pressure (float): Pore pressure in psi
        biot_coefficient (float): Biot coefficient (default 1.0)
        
    Returns:
        float: Effective stress in psi
    """
    sigma_total = total_stress
    pp = pore_pressure
    alpha = biot_coefficient
    
    sigma_eff = sigma_total - alpha * pp
    return sigma_eff


# =============================================================================
# ROCK MECHANICAL PROPERTIES
# =============================================================================

def bulk_modulus_from_lame(lame_constant: float, shear_modulus: float) -> float:
    """
    Calculate bulk modulus using Lame constants.
    
    Args:
        lame_constant (float): Lame's first parameter in psi
        shear_modulus (float): Shear modulus in psi
        
    Returns:
        float: Bulk modulus in psi
    """
    lam = lame_constant
    mu = shear_modulus
    
    k = lam + (2 * mu) / 3
    return k


def bulk_modulus_from_poisson_lame(
    poisson_ratio: float,
    lame_constant: float
) -> float:
    """
    Calculate bulk modulus using Poisson's ratio and Lame's constant.
    
    Args:
        poisson_ratio (float): Poisson's ratio (dimensionless)
        lame_constant (float): Lame's constant in psi
        
    Returns:
        float: Bulk modulus in psi
    """
    nu = poisson_ratio
    lam = lame_constant
    
    if (1 - 2*nu) == 0:
        raise ValueError("Invalid Poisson's ratio for bulk modulus calculation")
    
    k = lam * (1 + nu) / (3 * (1 - 2*nu))
    return k


def bulk_modulus_from_poisson_shear(
    poisson_ratio: float,
    shear_modulus: float
) -> float:
    """
    Calculate bulk modulus using Poisson's ratio and shear modulus.
    
    Args:
        poisson_ratio (float): Poisson's ratio (dimensionless)
        shear_modulus (float): Shear modulus in psi
        
    Returns:
        float: Bulk modulus in psi
    """
    nu = poisson_ratio
    mu = shear_modulus
    
    if (1 - 2*nu) == 0:
        raise ValueError("Invalid Poisson's ratio for bulk modulus calculation")
    
    k = (2 * mu * (1 + nu)) / (3 * (1 - 2*nu))
    return k


def shear_modulus_from_elastic_properties(
    youngs_modulus: float,
    poisson_ratio: float
) -> float:
    """
    Calculate shear modulus from Young's modulus and Poisson's ratio.
    
    Args:
        youngs_modulus (float): Young's modulus in psi
        poisson_ratio (float): Poisson's ratio (dimensionless)
        
    Returns:
        float: Shear modulus in psi
    """
    e = youngs_modulus
    nu = poisson_ratio
    
    if (1 + nu) == 0:
        raise ValueError("Invalid Poisson's ratio")
    
    mu = e / (2 * (1 + nu))
    return mu


def cohesive_strength_rocks(
    unconfined_compressive_strength: float,
    internal_friction_angle: float
) -> float:
    """
    Calculate cohesive strength of rocks.
    
    Args:
        unconfined_compressive_strength (float): Unconfined compressive strength in psi
        internal_friction_angle (float): Internal friction angle in degrees
        
    Returns:
        float: Cohesive strength in psi
    """
    ucs = unconfined_compressive_strength
    phi = math.radians(internal_friction_angle)
    
    c = ucs / (2 * math.sqrt(1 + math.sin(phi)**2) + 2 * math.sin(phi))
    return c


# =============================================================================
# FRACTURE CALCULATIONS
# =============================================================================

def fracture_gradient_eaton(
    overburden_gradient: float,
    pore_pressure_gradient: float,
    poisson_ratio: float
) -> float:
    """
    Calculate fracture gradient using Eaton method.
    
    Args:
        overburden_gradient (float): Overburden stress gradient in psi/ft
        pore_pressure_gradient (float): Pore pressure gradient in psi/ft
        poisson_ratio (float): Poisson's ratio (dimensionless)
        
    Returns:
        float: Fracture gradient in psi/ft
    """
    s_ob = overburden_gradient
    pp_grad = pore_pressure_gradient
    nu = poisson_ratio
    
    if (1 - nu) == 0:
        raise ValueError("Invalid Poisson's ratio")
    
    frac_grad = (nu / (1 - nu)) * (s_ob - pp_grad) + pp_grad
    return frac_grad


def fracture_gradient_matthews_kelly(
    overburden_gradient: float,
    pore_pressure_gradient: float,
    matrix_stress_coefficient: float = 0.5
) -> float:
    """
    Calculate fracture gradient using Matthews and Kelly method.
    
    Args:
        overburden_gradient (float): Overburden stress gradient in psi/ft
        pore_pressure_gradient (float): Pore pressure gradient in psi/ft
        matrix_stress_coefficient (float): Matrix stress coefficient, default 0.5
        
    Returns:
        float: Fracture gradient in psi/ft
    """
    s_ob = overburden_gradient
    pp_grad = pore_pressure_gradient
    k = matrix_stress_coefficient
    
    frac_grad = k * (s_ob - pp_grad) + pp_grad
    return frac_grad


def fracture_pressure_hubert_willis(
    overburden_stress: float,
    pore_pressure: float,
    poisson_ratio: float
) -> float:
    """
    Calculate fracture pressure using Hubert & Willis method.
    
    Args:
        overburden_stress (float): Overburden stress in psi
        pore_pressure (float): Pore pressure in psi
        poisson_ratio (float): Poisson's ratio (dimensionless)
        
    Returns:
        float: Fracture pressure in psi
    """
    s_v = overburden_stress
    pp = pore_pressure
    nu = poisson_ratio
    
    if (1 - nu) == 0:
        raise ValueError("Invalid Poisson's ratio")
    
    p_frac = (nu / (1 - nu)) * (s_v - pp) + pp
    return p_frac


def fracture_width_perkins_kern(
    fracture_height: float,
    injection_rate: float,
    fluid_viscosity: float,
    youngs_modulus: float,
    time: float
) -> float:
    """
    Calculate fracture width using Perkins and Kern method.
    
    Args:
        fracture_height (float): Fracture height in ft
        injection_rate (float): Injection rate in bbl/min
        fluid_viscosity (float): Fluid viscosity in cp
        youngs_modulus (float): Young's modulus in psi
        time (float): Time in minutes
        
    Returns:
        float: Fracture width in inches
    """
    h = fracture_height
    q = injection_rate * 5.615  # Convert bbl/min to ft³/min
    mu = fluid_viscosity
    e = youngs_modulus
    t = time
    
    if h == 0 or e == 0:
        raise ValueError("Fracture height and Young's modulus must be non-zero")
    
    # Perkins-Kern model (simplified)
    w = 2.5 * ((mu * q * t)**(1/4)) / ((e * h)**(1/4))
    
    # Convert ft to inches
    w_inches = w * 12
    return w_inches


def fracture_conductivity(
    fracture_width: float,
    proppant_permeability: float
) -> float:
    """
    Calculate fracture conductivity.
    
    Args:
        fracture_width (float): Fracture width in inches
        proppant_permeability (float): Proppant pack permeability in md
        
    Returns:
        float: Fracture conductivity in md·ft
    """
    w = fracture_width / 12  # Convert inches to ft
    k_f = proppant_permeability
    
    conductivity = k_f * w
    return conductivity


# =============================================================================
# FAILURE CRITERIA
# =============================================================================

def mohr_coulomb_failure_criterion(
    normal_stress: float,
    cohesive_strength: float,
    internal_friction_angle: float
) -> float:
    """
    Calculate shear stress at failure using Mohr-Coulomb criterion.
    
    Args:
        normal_stress (float): Normal stress in psi
        cohesive_strength (float): Cohesive strength in psi
        internal_friction_angle (float): Internal friction angle in degrees
        
    Returns:
        float: Shear stress at failure in psi
    """
    sigma_n = normal_stress
    c = cohesive_strength
    phi = math.radians(internal_friction_angle)
    
    tau = c + sigma_n * math.tan(phi)
    return tau


def hoek_brown_failure_criterion(
    major_principal_stress: float,
    minor_principal_stress: float,
    unconfined_compressive_strength: float,
    hoek_brown_constant_m: float,
    hoek_brown_constant_s: float
) -> bool:
    """
    Check failure using Hoek-Brown criterion.
    
    Args:
        major_principal_stress (float): Major principal stress in psi
        minor_principal_stress (float): Minor principal stress in psi
        unconfined_compressive_strength (float): Unconfined compressive strength in psi
        hoek_brown_constant_m (float): Hoek-Brown constant m
        hoek_brown_constant_s (float): Hoek-Brown constant s
        
    Returns:
        bool: True if failure occurs, False otherwise
    """
    sigma1 = major_principal_stress
    sigma3 = minor_principal_stress
    sigma_c = unconfined_compressive_strength
    m = hoek_brown_constant_m
    s = hoek_brown_constant_s
    
    # Hoek-Brown failure criterion
    lhs = sigma1 - sigma3
    rhs = sigma_c * math.sqrt(m * sigma3 / sigma_c + s)
    
    return lhs >= rhs


# =============================================================================
# SPECIALIZED CALCULATIONS
# =============================================================================

def formation_compressibility_hydrofrac(
    fracture_pressure: float,
    pore_pressure: float,
    overburden_stress: float
) -> float:
    """
    Calculate formation compressibility using hydrofrac data.
    
    Args:
        fracture_pressure (float): Fracture pressure in psi
        pore_pressure (float): Pore pressure in psi
        overburden_stress (float): Overburden stress in psi
        
    Returns:
        float: Formation compressibility in 1/psi
    """
    p_frac = fracture_pressure
    pp = pore_pressure
    s_v = overburden_stress
    
    if (s_v - pp) == 0:
        raise ValueError("Effective overburden stress cannot be zero")
    
    # Simplified relationship
    cf = 1 / (p_frac - pp)
    return cf


def pore_pressure_shale_fleming(
    depth: float,
    normal_compaction_trend: float,
    undercompaction_factor: float = 1.0
) -> float:
    """
    Calculate pore pressure in shale using Fleming's method.
    
    Args:
        depth (float): Depth in ft
        normal_compaction_trend (float): Normal compaction trend coefficient
        undercompaction_factor (float): Undercompaction factor, default 1.0
        
    Returns:
        float: Pore pressure in psi
    """
    d = depth
    nct = normal_compaction_trend
    ucf = undercompaction_factor
    
    # Fleming's empirical relationship
    pp = 0.433 * d + nct * d * ucf
    return pp


def breakdown_pressure_tensile_fracture(
    minimum_horizontal_stress: float,
    pore_pressure: float,
    tensile_strength: float
) -> float:
    """
    Calculate pressure required to induce tensile fracture (breakdown pressure).
    
    Args:
        minimum_horizontal_stress (float): Minimum horizontal stress in psi
        pore_pressure (float): Pore pressure in psi
        tensile_strength (float): Tensile strength of rock in psi
        
    Returns:
        float: Breakdown pressure in psi
    """
    sh_min = minimum_horizontal_stress
    pp = pore_pressure
    t0 = tensile_strength
    
    p_breakdown = 3 * sh_min - pp + t0
    return p_breakdown


def compressibility_coalbed_methane(
    porosity: float,
    cleat_compressibility: float,
    matrix_compressibility: float
) -> float:
    """
    Calculate compressibility of coalbed methane formation.
    
    Args:
        porosity (float): Porosity as fraction
        cleat_compressibility (float): Cleat system compressibility in 1/psi
        matrix_compressibility (float): Matrix compressibility in 1/psi
        
    Returns:
        float: Formation compressibility in 1/psi
    """
    phi = porosity
    cc = cleat_compressibility
    cm = matrix_compressibility
    
    cf = phi * cc + (1 - phi) * cm
    return cf


def deviated_borehole_axis(
    radius: float,
    position: float,
    azimuth: float,
    max_horizontal_stress: float,
    min_horizontal_stress: float,
    pore_pressure: float,
    thermal_stress: float = 0.0
) -> float:
    """
    Calculate axis stress of a deviated borehole from an arbitrary origin.
    
    Args:
        radius: Radius of Wellbore (ft)
        position: Position in Respect to Centre of Wellbore (ft)
        azimuth: Azimuth of Shmax (rad)
        max_horizontal_stress: Maximum Horizontal Stress (psi)
        min_horizontal_stress: Minimum Horizontal Stress (psi)
        pore_pressure: Pore Pressure (psi)
        thermal_stress: Thermal Stress (psi), default 0
    
    Returns:
        float: Axial stress (psi)
    
    Reference:
        Mark D. Zoback, Reservoir Geomechanics, Cambridge University Press, UK, Page: 170.
    """
    R2_r2 = (radius / position) ** 2
    R4_r4 = (radius / position) ** 4
    
    saa = (0.5 * (max_horizontal_stress + min_horizontal_stress - 2 * pore_pressure) * 
           (1 + R2_r2) - 
           0.5 * (max_horizontal_stress - min_horizontal_stress) * 
           (1 + 3 * R4_r4) * math.cos(2 * azimuth) - 
           pore_pressure * R2_r2 - thermal_stress)
    
    return saa


def change_pore_volume_expansion(
    initial_porosity: float,
    water_compressibility: float,
    rock_compressibility: float,
    pressure_change: float
) -> float:
    """
    Calculate change in pore volume due to initial water and rock expansion.
    
    Args:
        initial_porosity: Initial porosity (fraction)
        water_compressibility: Water compressibility (1/psi)
        rock_compressibility: Rock compressibility (1/psi)
        pressure_change: Pressure change (psi)
    
    Returns:
        float: Change in pore volume (fraction)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    dV_V = initial_porosity * (water_compressibility + rock_compressibility) * pressure_change
    return dV_V


def effect_pore_pressure_stress(
    effective_stress: float,
    pore_pressure: float,
    biot_coefficient: float = 1.0
) -> float:
    """
    Calculate effect of pore pressure on stress.
    
    Args:
        effective_stress: Effective stress (psi)
        pore_pressure: Pore pressure (psi)
        biot_coefficient: Biot coefficient (dimensionless), default 1.0
    
    Returns:
        float: Total stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    total_stress = effective_stress + biot_coefficient * pore_pressure
    return total_stress


def m_modulus_shear_bulk(
    shear_modulus: float,
    bulk_modulus: float
) -> float:
    """
    Calculate M modulus using shear modulus and bulk modulus.
    
    Args:
        shear_modulus: Shear modulus (Pa)
        bulk_modulus: Bulk modulus (Pa)
    
    Returns:
        float: M modulus (Pa)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    M = bulk_modulus + (4.0/3.0) * shear_modulus
    return M


def m_modulus_youngs_poisson(
    youngs_modulus: float,
    poisson_ratio: float
) -> float:
    """
    Calculate M modulus using Young's modulus and Poisson's ratio.
    
    Args:
        youngs_modulus: Young's modulus (Pa)
        poisson_ratio: Poisson's ratio (dimensionless)
    
    Returns:
        float: M modulus (Pa)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    M = youngs_modulus * (1 - poisson_ratio) / ((1 + poisson_ratio) * (1 - 2 * poisson_ratio))
    return M


def fracture_gradient_holbrook(
    depth: float,
    matrix_stress_coefficient: float = 0.33
) -> float:
    """
    Calculate fracture gradient using Holbrook method.
    
    Args:
        depth: Depth (ft)
        matrix_stress_coefficient: Matrix stress coefficient (dimensionless), default 0.33
    
    Returns:
        float: Fracture gradient (psi/ft)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    fracture_gradient = 0.052 * depth**0.025 + matrix_stress_coefficient
    return fracture_gradient


def fracture_gradient_zoback_healy(
    overburden_gradient: float,
    pore_pressure_gradient: float,
    poisson_ratio: float
) -> float:
    """
    Calculate fracture gradient using Zoback and Healy method.
    
    Args:
        overburden_gradient: Overburden gradient (psi/ft)
        pore_pressure_gradient: Pore pressure gradient (psi/ft)
        poisson_ratio: Poisson's ratio (dimensionless)
    
    Returns:
        float: Fracture gradient (psi/ft)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    stress_ratio = poisson_ratio / (1 - poisson_ratio)
    fracture_gradient = pore_pressure_gradient + stress_ratio * (overburden_gradient - pore_pressure_gradient)
    return fracture_gradient


def fracture_volume_gdk_method(
    fracture_height: float,
    fracture_length: float,
    average_width: float
) -> float:
    """
    Calculate fracture volume using GDK method.
    
    Args:
        fracture_height: Fracture height (ft)
        fracture_length: Fracture length (ft)
        average_width: Average fracture width (in)
    
    Returns:
        float: Fracture volume (ft³)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    volume = fracture_height * fracture_length * (average_width / 12.0)
    return volume


def fracture_volume_perkins_kern(
    fracture_height: float,
    fracture_length: float,
    max_width: float
) -> float:
    """
    Calculate fracture volume using Perkins and Kern method.
    
    Args:
        fracture_height: Fracture height (ft)
        fracture_length: Fracture length (ft)
        max_width: Maximum fracture width (in)
    
    Returns:
        float: Fracture volume (ft³)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    volume = (2.0/3.0) * fracture_height * fracture_length * (max_width / 12.0)
    return volume


def fracture_width_gdk_method(
    net_pressure: float,
    fracture_height: float,
    youngs_modulus: float,
    poisson_ratio: float
) -> float:
    """
    Calculate fracture width using GDK method.
    
    Args:
        net_pressure: Net pressure in fracture (psi)
        fracture_height: Fracture height (ft)
        youngs_modulus: Young's modulus (psi)
        poisson_ratio: Poisson's ratio (dimensionless)
    
    Returns:
        float: Fracture width (in)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    shear_modulus = youngs_modulus / (2 * (1 + poisson_ratio))
    width = (2 * net_pressure * fracture_height) / shear_modulus
    return width * 12.0  # Convert ft to inches


def horizontal_effective_stress_lorenz_teufel(
    vertical_stress: float,
    pore_pressure: float,
    poisson_ratio: float
) -> float:
    """
    Calculate horizontal effective stress assuming no lateral strain (Lorenz and Teufel).
    
    Args:
        vertical_stress: Vertical stress (psi)
        pore_pressure: Pore pressure (psi)
        poisson_ratio: Poisson's ratio (dimensionless)
    
    Returns:
        float: Horizontal effective stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    stress_ratio = poisson_ratio / (1 - poisson_ratio)
    horizontal_stress = stress_ratio * (vertical_stress - pore_pressure) + pore_pressure
    return horizontal_stress


def horizontal_maximum_stress_bredehoeft(
    depth: float,
    fluid_density: float = 9.0
) -> float:
    """
    Calculate horizontal maximum stress using Bredehoeft method.
    
    Args:
        depth: Depth (ft)
        fluid_density: Fluid density (ppg), default 9.0
    
    Returns:
        float: Horizontal maximum stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    stress = 0.052 * fluid_density * depth * 1.25  # 1.25 is stress concentration factor
    return stress


def induced_fracture_dip(
    maximum_horizontal_stress: float,
    minimum_horizontal_stress: float,
    vertical_stress: float
) -> float:
    """
    Calculate induced fracture dip angle.
    
    Args:
        maximum_horizontal_stress: Maximum horizontal stress (psi)
        minimum_horizontal_stress: Minimum horizontal stress (psi)
        vertical_stress: Vertical stress (psi)
    
    Returns:
        float: Fracture dip angle (degrees)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    if maximum_horizontal_stress > vertical_stress:
        # Vertical fracture
        dip = 90.0
    else:
        # Horizontal fracture
        dip = 0.0
    return dip


def initial_effective_horizontal_stress(
    total_horizontal_stress: float,
    initial_pore_pressure: float,
    biot_coefficient: float = 1.0
) -> float:
    """
    Calculate initial effective horizontal stress.
    
    Args:
        total_horizontal_stress: Total horizontal stress (psi)
        initial_pore_pressure: Initial pore pressure (psi)
        biot_coefficient: Biot coefficient (dimensionless), default 1.0
    
    Returns:
        float: Initial effective horizontal stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    effective_stress = total_horizontal_stress - biot_coefficient * initial_pore_pressure
    return effective_stress


def isothermal_compressibility_limestone_newman(
    porosity: float
) -> float:
    """
    Calculate isothermal compressibility of limestones using Newman correlation.
    
    Args:
        porosity: Porosity (fraction)
    
    Returns:
        float: Compressibility (1/psi × 10⁻⁶)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas (Newman correlation)
    """
    # Newman correlation for limestone
    compressibility = 0.8543 + 17.312 * porosity  # × 10⁻⁶ /psi
    return compressibility


def least_principal_stress_gulf_mexico_hubbert_willis(
    depth: float
) -> float:
    """
    Calculate least principal stress as function of depth in Gulf of Mexico (Hubbert & Willis).
    
    Args:
        depth: Depth (ft)
    
    Returns:
        float: Least principal stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas (Hubbert & Willis)
    """
    stress = 0.465 * depth + 340
    return stress


def least_principal_stress_gulf_mexico_matthews_kelly(
    depth: float
) -> float:
    """
    Calculate least principal stress as function of depth in Gulf of Mexico (Matthews & Kelly).
    
    Args:
        depth: Depth (ft)
    
    Returns:
        float: Least principal stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas (Matthews & Kelly)
    """
    if depth <= 8000:
        stress = 0.052 * 15.8 * depth  # 15.8 ppg equivalent
    else:
        stress = 0.052 * 18.0 * depth  # 18.0 ppg equivalent
    return stress


def linearized_mohr_failure_line(
    cohesive_strength: float,
    friction_angle: float,
    normal_stress: float
) -> float:
    """
    Calculate linearized Mohr failure line.
    
    Args:
        cohesive_strength: Cohesive strength (psi)
        friction_angle: Internal friction angle (degrees)
        normal_stress: Normal stress (psi)
    
    Returns:
        float: Shear stress at failure (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    friction_angle_rad = math.radians(friction_angle)
    shear_stress = cohesive_strength + normal_stress * math.tan(friction_angle_rad)
    return shear_stress


def linearized_mohr_coulomb_criteria(
    normal_stress: float,
    cohesive_strength: float,
    friction_coefficient: float
) -> float:
    """
    Calculate linearized Mohr-Coulomb failure criteria.
    
    Args:
        normal_stress: Normal stress (psi)
        cohesive_strength: Cohesive strength (psi)
        friction_coefficient: Friction coefficient (dimensionless)
    
    Returns:
        float: Shear stress at failure (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    shear_stress = cohesive_strength + friction_coefficient * normal_stress
    return shear_stress


def maximum_anisotropic_failure_stress(
    unconfined_compressive_strength: float,
    anisotropy_factor: float,
    confining_pressure: float
) -> float:
    """
    Calculate maximum anisotropic failure stress.
    
    Args:
        unconfined_compressive_strength: Unconfined compressive strength (psi)
        anisotropy_factor: Anisotropy factor (dimensionless)
        confining_pressure: Confining pressure (psi)
    
    Returns:
        float: Maximum anisotropic failure stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    failure_stress = unconfined_compressive_strength * anisotropy_factor + 2 * confining_pressure
    return failure_stress


def maximum_compression_vertical_wellbore(
    max_horizontal_stress: float,
    min_horizontal_stress: float,
    pore_pressure: float,
    mud_weight: float,
    depth: float
) -> float:
    """
    Calculate maximum compression at vertical wellbore.
    
    Args:
        max_horizontal_stress: Maximum horizontal stress (psi)
        min_horizontal_stress: Minimum horizontal stress (psi)
        pore_pressure: Pore pressure (psi)
        mud_weight: Mud weight (ppg)
        depth: Depth (ft)
    
    Returns:
        float: Maximum compression stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    mud_pressure = 0.052 * mud_weight * depth
    max_compression = 3 * min_horizontal_stress - max_horizontal_stress + mud_pressure - pore_pressure
    return max_compression


def maximum_normal_stress_tangential_wellbore(
    max_horizontal_stress: float,
    min_horizontal_stress: float,
    wellbore_pressure: float,
    azimuth: float = 0.0
) -> float:
    """
    Calculate maximum normal stress in tangential direction at wellbore wall (hoop stress).
    
    Args:
        max_horizontal_stress: Maximum horizontal stress (psi)
        min_horizontal_stress: Minimum horizontal stress (psi)
        wellbore_pressure: Wellbore pressure (psi)
        azimuth: Azimuth angle (rad), default 0
    
    Returns:
        float: Maximum tangential stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    mean_stress = (max_horizontal_stress + min_horizontal_stress) / 2
    stress_difference = (max_horizontal_stress - min_horizontal_stress) / 2
    
    max_tangential = mean_stress + stress_difference * math.cos(2 * azimuth) - wellbore_pressure
    return max_tangential


def maximum_principal_stress_normal_faulting(
    minimum_principal_stress: float,
    friction_coefficient: float
) -> float:
    """
    Calculate maximum principal stress in normal faulting.
    
    Args:
        minimum_principal_stress: Minimum principal stress (psi)
        friction_coefficient: Friction coefficient (dimensionless)
    
    Returns:
        float: Maximum principal stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    max_stress = minimum_principal_stress * ((math.sqrt(1 + friction_coefficient**2) + friction_coefficient)**2)
    return max_stress


def maximum_principal_stress_reverse_faulting(
    minimum_principal_stress: float,
    friction_coefficient: float
) -> float:
    """
    Calculate maximum principal stress in reverse faulting.
    
    Args:
        minimum_principal_stress: Minimum principal stress (psi)
        friction_coefficient: Friction coefficient (dimensionless)
    
    Returns:
        float: Maximum principal stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    max_stress = minimum_principal_stress * ((math.sqrt(1 + friction_coefficient**2) + 1/friction_coefficient)**2)
    return max_stress


def maximum_principal_stress_strike_slip_faulting(
    minimum_principal_stress: float,
    friction_coefficient: float
) -> float:
    """
    Calculate maximum principal stress in strike-slip faulting.
    
    Args:
        minimum_principal_stress: Minimum principal stress (psi)
        friction_coefficient: Friction coefficient (dimensionless)
    
    Returns:
        float: Maximum principal stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    phi = math.atan(friction_coefficient)
    max_stress = minimum_principal_stress * (1 + math.sin(phi)) / (1 - math.sin(phi))
    return max_stress


def maximum_principal_stress_breakout_width(
    breakout_width: float,
    wellbore_radius: float,
    min_horizontal_stress: float,
    wellbore_pressure: float,
    rock_strength: float
) -> float:
    """
    Calculate maximum principal stress using breakout width.
    
    Args:
        breakout_width: Breakout width (degrees)
        wellbore_radius: Wellbore radius (ft)
        min_horizontal_stress: Minimum horizontal stress (psi)
        wellbore_pressure: Wellbore pressure (psi)
        rock_strength: Rock compressive strength (psi)
    
    Returns:
        float: Maximum principal stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    # Convert breakout width to radians
    theta = math.radians(breakout_width / 2)
    
    # Calculate stress concentration factor
    stress_factor = 2 * (1 + math.cos(2 * theta))
    
    max_stress = (rock_strength + wellbore_pressure - stress_factor * min_horizontal_stress) / (stress_factor - 2)
    return max_stress


def minimum_compression_vertical_wellbore(
    max_horizontal_stress: float,
    min_horizontal_stress: float,
    pore_pressure: float,
    mud_weight: float,
    depth: float
) -> float:
    """
    Calculate minimum compression at vertical wellbore.
    
    Args:
        max_horizontal_stress: Maximum horizontal stress (psi)
        min_horizontal_stress: Minimum horizontal stress (psi)
        pore_pressure: Pore pressure (psi)
        mud_weight: Mud weight (ppg)
        depth: Depth (ft)
    
    Returns:
        float: Minimum compression stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    mud_pressure = 0.052 * mud_weight * depth
    min_compression = 3 * max_horizontal_stress - min_horizontal_stress + mud_pressure - pore_pressure
    return min_compression


def minimum_normal_stress_tangential_wellbore(
    max_horizontal_stress: float,
    min_horizontal_stress: float,
    wellbore_pressure: float,
    azimuth: float = math.pi/2
) -> float:
    """
    Calculate minimum normal stress in tangential direction at wellbore wall (hoop stress).
    
    Args:
        max_horizontal_stress: Maximum horizontal stress (psi)
        min_horizontal_stress: Minimum horizontal stress (psi)
        wellbore_pressure: Wellbore pressure (psi)
        azimuth: Azimuth angle (rad), default π/2
    
    Returns:
        float: Minimum tangential stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    mean_stress = (max_horizontal_stress + min_horizontal_stress) / 2
    stress_difference = (max_horizontal_stress - min_horizontal_stress) / 2
    
    min_tangential = mean_stress - stress_difference * math.cos(2 * azimuth) - wellbore_pressure
    return min_tangential


def modified_lade_criterion(
    first_invariant: float,
    third_invariant: float,
    m_parameter: float = 27.0
) -> float:
    """
    Calculate modified Lade failure criterion.
    
    Args:
        first_invariant: First stress invariant (psi)
        third_invariant: Third stress invariant (psi³)
        m_parameter: Material parameter (dimensionless), default 27.0
    
    Returns:
        float: Lade criterion value (psi³)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    criterion = (first_invariant**3 / third_invariant) - m_parameter
    return criterion


def normal_stress_radial_direction_wellbore(
    wellbore_pressure: float
) -> float:
    """
    Calculate normal stress in radial direction near wellbore.
    
    Args:
        wellbore_pressure: Wellbore pressure (psi)
    
    Returns:
        float: Radial stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    # At wellbore wall, radial stress equals wellbore pressure
    radial_stress = wellbore_pressure
    return radial_stress


def normal_stress_rock_failure(
    shear_stress: float,
    cohesive_strength: float,
    friction_angle: float
) -> float:
    """
    Calculate normal stress in rock at failure.
    
    Args:
        shear_stress: Shear stress (psi)
        cohesive_strength: Cohesive strength (psi)
        friction_angle: Internal friction angle (degrees)
    
    Returns:
        float: Normal stress at failure (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    friction_angle_rad = math.radians(friction_angle)
    normal_stress = (shear_stress - cohesive_strength) / math.tan(friction_angle_rad)
    return normal_stress


def normal_stress_tangential_direction_near_wellbore(
    max_horizontal_stress: float,
    min_horizontal_stress: float,
    wellbore_pressure: float,
    radius_ratio: float,
    azimuth: float
) -> float:
    """
    Calculate normal stress in tangential direction near wellbore (hoop stress).
    
    Args:
        max_horizontal_stress: Maximum horizontal stress (psi)
        min_horizontal_stress: Minimum horizontal stress (psi)
        wellbore_pressure: Wellbore pressure (psi)
        radius_ratio: Radius ratio (wellbore_radius/position_radius)
        azimuth: Azimuth angle (rad)
    
    Returns:
        float: Tangential stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    mean_stress = (max_horizontal_stress + min_horizontal_stress) / 2
    stress_difference = (max_horizontal_stress - min_horizontal_stress) / 2
    
    tangential_stress = (mean_stress * (1 + radius_ratio**2) + 
                        stress_difference * (1 + 3 * radius_ratio**4) * math.cos(2 * azimuth) -
                        wellbore_pressure * radius_ratio**2)
    
    return tangential_stress


def pore_pressure_increase_mody_hale(
    activity_contrast: float,
    temperature: float,
    membrane_efficiency: float = 0.5
) -> float:
    """
    Calculate pore pressure increase due to fluid activity (Mody & Hale).
    
    Args:
        activity_contrast: Activity contrast (dimensionless)
        temperature: Temperature (°F)
        membrane_efficiency: Membrane efficiency (dimensionless), default 0.5
    
    Returns:
        float: Pore pressure increase (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas (Mody & Hale)
    """
    # Convert temperature to absolute scale
    temp_rankine = temperature + 459.67
    
    # Gas constant for pressure in psi
    R = 10.73  # psi·ft³/(lbmol·°R)
    
    # Calculate osmotic pressure
    osmotic_pressure = membrane_efficiency * R * temp_rankine * math.log(1 + activity_contrast)
    
    return osmotic_pressure


def pore_pressure_increase_activity_contrast(
    osmotic_coefficient: float,
    activity_contrast: float,
    temperature: float
) -> float:
    """
    Calculate pore pressure increase due to given fluid activity contrast.
    
    Args:
        osmotic_coefficient: Osmotic coefficient (dimensionless)
        activity_contrast: Activity contrast (dimensionless)
        temperature: Temperature (°F)
    
    Returns:
        float: Pore pressure increase (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    # Convert temperature to absolute scale
    temp_rankine = temperature + 459.67
    
    # Gas constant
    R = 10.73  # psi·ft³/(lbmol·°R)
    
    pressure_increase = osmotic_coefficient * R * temp_rankine * activity_contrast
    return pressure_increase


def pore_pressure_shale_traugott(
    depth: float,
    surface_porosity: float = 0.4,
    compaction_coefficient: float = 0.000285
) -> float:
    """
    Calculate pore pressure of shale using Traugott method.
    
    Args:
        depth: Depth (ft)
        surface_porosity: Surface porosity (fraction), default 0.4
        compaction_coefficient: Compaction coefficient (1/ft), default 0.000285
    
    Returns:
        float: Pore pressure (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas (Traugott)
    """
    porosity = surface_porosity * math.exp(-compaction_coefficient * depth)
    pore_pressure = 0.052 * 9.0 * depth * (1 + porosity)  # 9.0 ppg equivalent
    return pore_pressure


def porosity_irreversible_plastic_deformation(
    initial_porosity: float,
    stress_increase: float,
    yield_stress: float,
    compaction_coefficient: float
) -> float:
    """
    Calculate porosity when irreversible plastic deformation occurs.
    
    Args:
        initial_porosity: Initial porosity (fraction)
        stress_increase: Stress increase (psi)
        yield_stress: Yield stress (psi)
        compaction_coefficient: Compaction coefficient (1/psi)
    
    Returns:
        float: Final porosity (fraction)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    if stress_increase > yield_stress:
        excess_stress = stress_increase - yield_stress
        porosity = initial_porosity * math.exp(-compaction_coefficient * excess_stress)
    else:
        porosity = initial_porosity
    
    return porosity


def pressure_grow_fractures_abe_mura(
    initial_crack_length: float,
    stress_intensity_factor: float,
    material_toughness: float,
    applied_stress: float
) -> float:
    """
    Calculate pressure to grow fractures (Abe, Mura, et al.).
    
    Args:
        initial_crack_length: Initial crack length (ft)
        stress_intensity_factor: Stress intensity factor (psi·√ft)
        material_toughness: Material fracture toughness (psi·√ft)
        applied_stress: Applied stress (psi)
    
    Returns:
        float: Pressure to grow fractures (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas (Abe, Mura, et al.)
    """
    crack_pressure = (material_toughness / (stress_intensity_factor * math.sqrt(math.pi * initial_crack_length))) - applied_stress
    return crack_pressure


def ratio_pore_pressure_change_depletion(
    current_pressure: float,
    initial_pressure: float
) -> float:
    """
    Calculate ratio of pore pressure change to original due to depletion.
    
    Args:
        current_pressure: Current pore pressure (psi)
        initial_pressure: Initial pore pressure (psi)
    
    Returns:
        float: Pressure ratio (dimensionless)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    pressure_ratio = (initial_pressure - current_pressure) / initial_pressure
    return pressure_ratio


def rotation_maximum_principal_stress_wellbore(
    distance_from_wellbore: float,
    wellbore_radius: float,
    stress_difference: float,
    mean_stress: float
) -> float:
    """
    Calculate rotation of maximum principal stress near wellbore.
    
    Args:
        distance_from_wellbore: Distance from wellbore (ft)
        wellbore_radius: Wellbore radius (ft)
        stress_difference: Stress difference (psi)
        mean_stress: Mean stress (psi)
    
    Returns:
        float: Rotation angle (radians)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    radius_ratio = wellbore_radius / distance_from_wellbore
    rotation = math.atan(2 * radius_ratio**2 * stress_difference / mean_stress)
    return rotation


def rotation_maximum_principal_stress_zoback_day_lewis(
    radial_distance: float,
    wellbore_radius: float,
    horizontal_stress_difference: float
) -> float:
    """
    Calculate rotation of maximum principal stress near wellbore (Zoback & Day-Lewis).
    
    Args:
        radial_distance: Radial distance from wellbore (ft)
        wellbore_radius: Wellbore radius (ft)
        horizontal_stress_difference: Horizontal stress difference (psi)
    
    Returns:
        float: Rotation angle (degrees)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas (Zoback & Day-Lewis)
    """
    r_ratio = wellbore_radius / radial_distance
    rotation_rad = 0.5 * math.atan(2 * r_ratio**2)
    rotation_deg = math.degrees(rotation_rad)
    return rotation_deg


def shale_compaction(
    initial_thickness: float,
    pressure_decline: float,
    compaction_coefficient: float
) -> float:
    """
    Calculate shale compaction.
    
    Args:
        initial_thickness: Initial thickness (ft)
        pressure_decline: Pressure decline (psi)
        compaction_coefficient: Compaction coefficient (1/psi)
    
    Returns:
        float: Compaction (ft)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    compaction = initial_thickness * compaction_coefficient * pressure_decline
    return compaction


def shear_modulus_from_youngs_modulus(
    youngs_modulus: float,
    poisson_ratio: float
) -> float:
    """
    Calculate shear modulus from Young's modulus.
    
    Args:
        youngs_modulus: Young's modulus (Pa)
        poisson_ratio: Poisson's ratio (dimensionless)
    
    Returns:
        float: Shear modulus (Pa)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    shear_modulus = youngs_modulus / (2 * (1 + poisson_ratio))
    return shear_modulus


def shear_stress_near_vertical_well(
    max_horizontal_stress: float,
    min_horizontal_stress: float,
    radius_ratio: float,
    azimuth: float
) -> float:
    """
    Calculate shear stress near vertical well.
    
    Args:
        max_horizontal_stress: Maximum horizontal stress (psi)
        min_horizontal_stress: Minimum horizontal stress (psi)
        radius_ratio: Radius ratio (wellbore_radius/position_radius)
        azimuth: Azimuth angle (rad)
    
    Returns:
        float: Shear stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    stress_difference = (max_horizontal_stress - min_horizontal_stress) / 2
    shear_stress = -stress_difference * (1 + 3 * radius_ratio**4) * math.sin(2 * azimuth)
    return shear_stress


def slowness_formation(
    travel_time: float,
    formation_thickness: float
) -> float:
    """
    Calculate slowness of the formation.
    
    Args:
        travel_time: Travel time (μs)
        formation_thickness: Formation thickness (ft)
    
    Returns:
        float: Slowness (μs/ft)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    slowness = travel_time / formation_thickness
    return slowness


def storativity_fractures(
    fracture_compressibility: float,
    fluid_compressibility: float,
    fracture_porosity: float
) -> float:
    """
    Calculate storativity of fractures.
    
    Args:
        fracture_compressibility: Fracture compressibility (1/psi)
        fluid_compressibility: Fluid compressibility (1/psi)
        fracture_porosity: Fracture porosity (fraction)
    
    Returns:
        float: Storativity (1/psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    storativity = fracture_porosity * (fracture_compressibility + fluid_compressibility)
    return storativity


def stress_edge_wellbore_breakout(
    tangential_stress: float,
    radial_stress: float,
    compressive_strength: float
) -> float:
    """
    Calculate stress at edge of wellbore breakout.
    
    Args:
        tangential_stress: Tangential stress (psi)
        radial_stress: Radial stress (psi)
        compressive_strength: Rock compressive strength (psi)
    
    Returns:
        float: Stress at breakout edge (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    effective_stress = tangential_stress - radial_stress
    if effective_stress >= compressive_strength:
        breakout_stress = effective_stress
    else:
        breakout_stress = 0.0
    return breakout_stress


def stress_component_normal_faulting_reservoir(
    vertical_stress: float,
    horizontal_stress: float,
    pore_pressure: float,
    fault_angle: float
) -> Tuple[float, float]:
    """
    Calculate stress component near normal faulting in reservoir.
    
    Args:
        vertical_stress: Vertical stress (psi)
        horizontal_stress: Horizontal stress (psi)
        pore_pressure: Pore pressure (psi)
        fault_angle: Fault angle (degrees)
    
    Returns:
        Tuple[float, float]: Normal stress and shear stress on fault plane (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    fault_angle_rad = math.radians(fault_angle)
    
    # Stress tensor rotation
    normal_stress = (vertical_stress * math.cos(fault_angle_rad)**2 + 
                    horizontal_stress * math.sin(fault_angle_rad)**2 - pore_pressure)
    
    shear_stress = (vertical_stress - horizontal_stress) * math.sin(fault_angle_rad) * math.cos(fault_angle_rad)
    
    return normal_stress, shear_stress


def stress_components_depletion_drive(
    initial_horizontal_stress: float,
    initial_vertical_stress: float,
    pressure_decline: float,
    rock_compressibility: float,
    poisson_ratio: float
) -> Tuple[float, float]:
    """
    Calculate stress components in original coordinate system in depletion drive.
    
    Args:
        initial_horizontal_stress: Initial horizontal stress (psi)
        initial_vertical_stress: Initial vertical stress (psi)
        pressure_decline: Pressure decline (psi)
        rock_compressibility: Rock compressibility (1/psi)
        poisson_ratio: Poisson's ratio (dimensionless)
    
    Returns:
        Tuple[float, float]: Current horizontal and vertical stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    # Stress change due to pressure depletion
    stress_change_horizontal = pressure_decline * poisson_ratio / (1 - poisson_ratio)
    stress_change_vertical = pressure_decline
    
    current_horizontal_stress = initial_horizontal_stress + stress_change_horizontal
    current_vertical_stress = initial_vertical_stress + stress_change_vertical
    
    return current_horizontal_stress, current_vertical_stress


def stress_intensity_tip_mode_i_fracture(
    applied_stress: float,
    crack_length: float
) -> float:
    """
    Calculate stress intensity at tip of mode I fracture.
    
    Args:
        applied_stress: Applied stress (psi)
        crack_length: Crack length (ft)
    
    Returns:
        float: Stress intensity factor (psi·√ft)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    stress_intensity = applied_stress * math.sqrt(math.pi * crack_length)
    return stress_intensity


def stress_path_induced_normal_faulting(
    effective_vertical_stress: float,
    effective_horizontal_stress: float,
    pressure_change: float
) -> Tuple[float, float]:
    """
    Calculate stress path for induced normal faulting.
    
    Args:
        effective_vertical_stress: Effective vertical stress (psi)
        effective_horizontal_stress: Effective horizontal stress (psi)
        pressure_change: Pressure change (psi)
    
    Returns:
        Tuple[float, float]: New effective vertical and horizontal stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    new_vertical_stress = effective_vertical_stress + pressure_change
    new_horizontal_stress = effective_horizontal_stress + pressure_change
    
    return new_vertical_stress, new_horizontal_stress


def stress_path_reservoir_production_change(
    initial_mean_stress: float,
    initial_deviatoric_stress: float,
    pressure_change: float,
    stress_path_parameter: float = 1.0
) -> Tuple[float, float]:
    """
    Calculate stress path of reservoir with changes in production.
    
    Args:
        initial_mean_stress: Initial mean effective stress (psi)
        initial_deviatoric_stress: Initial deviatoric stress (psi)
        pressure_change: Pressure change (psi)
        stress_path_parameter: Stress path parameter (dimensionless), default 1.0
    
    Returns:
        Tuple[float, float]: New mean stress and deviatoric stress (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    new_mean_stress = initial_mean_stress + pressure_change
    new_deviatoric_stress = initial_deviatoric_stress + stress_path_parameter * pressure_change
    
    return new_mean_stress, new_deviatoric_stress


def stress_perturbation_segall_fitzgerald(
    fault_slip: float,
    shear_modulus: float,
    fault_length: float,
    distance_from_fault: float
) -> float:
    """
    Calculate stress perturbation (Segall and Fitzgerald).
    
    Args:
        fault_slip: Fault slip (ft)
        shear_modulus: Shear modulus (psi)
        fault_length: Fault length (ft)
        distance_from_fault: Distance from fault (ft)
    
    Returns:
        float: Stress perturbation (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas (Segall and Fitzgerald)
    """
    stress_perturbation = (shear_modulus * fault_slip) / (2 * math.pi * distance_from_fault) * (fault_length / distance_from_fault)
    return stress_perturbation


def subsidence_uniform_pore_pressure_reduction(
    thickness: float,
    pressure_decline: float,
    bulk_compressibility: float,
    depth: float
) -> float:
    """
    Calculate subsidence due to uniform pore pressure reduction in free surfaces.
    
    Args:
        thickness: Formation thickness (ft)
        pressure_decline: Pressure decline (psi)
        bulk_compressibility: Bulk compressibility (1/psi)
        depth: Depth to formation (ft)
    
    Returns:
        float: Subsidence (ft)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    subsidence = thickness * pressure_decline * bulk_compressibility * (1 - depth/10000)  # Depth factor
    return subsidence


def unconfined_compressive_strength_rock(
    cohesive_strength: float,
    friction_angle: float
) -> float:
    """
    Calculate unconfined compressive strength of rock.
    
    Args:
        cohesive_strength: Cohesive strength (psi)
        friction_angle: Internal friction angle (degrees)
    
    Returns:
        float: Unconfined compressive strength (psi)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    friction_angle_rad = math.radians(friction_angle)
    ucs = 2 * cohesive_strength * math.cos(friction_angle_rad) / (1 - math.sin(friction_angle_rad))
    return ucs


def velocity_bulk_compressional_waves(
    bulk_modulus: float,
    density: float
) -> float:
    """
    Calculate velocity of bulk compressional waves.
    
    Args:
        bulk_modulus: Bulk modulus (Pa)
        density: Density (kg/m³)
    
    Returns:
        float: Velocity (m/s)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    velocity = math.sqrt(bulk_modulus / density)
    return velocity


def velocity_compression_waves(
    youngs_modulus: float,
    poisson_ratio: float,
    density: float
) -> float:
    """
    Calculate velocity of compression waves.
    
    Args:
        youngs_modulus: Young's modulus (Pa)
        poisson_ratio: Poisson's ratio (dimensionless)
        density: Density (kg/m³)
    
    Returns:
        float: P-wave velocity (m/s)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    factor = (1 - poisson_ratio) / ((1 + poisson_ratio) * (1 - 2 * poisson_ratio))
    velocity = math.sqrt(youngs_modulus * factor / density)
    return velocity


def velocity_shear_waves(
    shear_modulus: float,
    density: float
) -> float:
    """
    Calculate velocity of shear waves.
    
    Args:
        shear_modulus: Shear modulus (Pa)
        density: Density (kg/m³)
    
    Returns:
        float: S-wave velocity (m/s)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    velocity = math.sqrt(shear_modulus / density)
    return velocity


def vp_vs_calculation_eberhart_phillips(
    porosity: float,
    clay_content: float,
    effective_pressure: float
) -> Tuple[float, float]:
    """
    Calculate Vp and Vs using Eberhart-Phillips correlation.
    
    Args:
        porosity: Porosity (fraction)
        clay_content: Clay content (fraction)
        effective_pressure: Effective pressure (kPa)
    
    Returns:
        Tuple[float, float]: P-wave and S-wave velocities (km/s)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas (Eberhart-Phillips)
    """
    # Eberhart-Phillips correlation
    vp = 5.77 - 6.94 * porosity - 1.73 * math.sqrt(clay_content) + 0.446 * (effective_pressure / 1000.0 - math.exp(-16.7 / 1000.0 * effective_pressure))
    
    # Vs from Vp using typical rock relations
    vs = vp / 1.73  # Approximate Vp/Vs ratio for sedimentary rocks
    
    return vp, vs


def vp_vs_calculation_geomechanical_model(
    effective_pressure: float,
    porosity: float,
    shale_volume: float
) -> Tuple[float, float]:
    """
    Calculate Vp and Vs using geomechanical model.
    
    Args:
        effective_pressure: Effective pressure (psi)
        porosity: Porosity (fraction)
        shale_volume: Shale volume (fraction)
    
    Returns:
        Tuple[float, float]: P-wave and S-wave velocities (ft/s)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    # Convert pressure to kPa for calculation
    eff_pressure_kpa = effective_pressure * 6.895
    
    # Simplified geomechanical model
    vp_sandstone = 5500 + 2.3 * eff_pressure_kpa**0.5 - 1800 * porosity
    vp_shale = 3500 + 1.8 * eff_pressure_kpa**0.5 - 1200 * porosity
    
    vp = vp_sandstone * (1 - shale_volume) + vp_shale * shale_volume
    vs = vp / 1.8  # Typical Vp/Vs ratio
    
    return vp, vs


def yield_strength_bingham_plastic(
    plastic_viscosity: float,
    shear_rate: float,
    yield_point: float
) -> float:
    """
    Calculate yield strength using Bingham plastic model.
    
    Args:
        plastic_viscosity: Plastic viscosity (cp)
        shear_rate: Shear rate (1/s)
        yield_point: Yield point (lbf/100ft²)
    
    Returns:
        float: Shear stress (lbf/100ft²)
    
    Reference:
        Chapter 11 - Geomechanics and fracturing formulas
    """
    shear_stress = yield_point + plastic_viscosity * shear_rate
    return shear_stress
