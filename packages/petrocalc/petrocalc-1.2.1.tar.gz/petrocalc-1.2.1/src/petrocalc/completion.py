"""
Well completion and stimulation calculations.

This module contains functions for completion and stimulation calculations including:
- Perforation design and performance
- Hydraulic fracturing calculations
- Acidizing calculations
- Sand control design
- Completion optimization
"""

import math
from typing import Union, Tuple, Optional


def perforation_flow_efficiency(
    perforation_diameter: float,
    wellbore_diameter: float,
    shots_per_foot: float,
    penetration_depth: float,
    phasing_angle: float = 60
) -> float:
    """
    Calculates perforation flow efficiency.
    
    Args:
        perforation_diameter (float): Perforation diameter in inches
        wellbore_diameter (float): Wellbore diameter in inches
        shots_per_foot (float): Number of shots per foot
        penetration_depth (float): Penetration depth in inches
        phasing_angle (float): Phasing angle in degrees (default 60)
        
    Returns:
        float: Flow efficiency (dimensionless)
    """
    dp = perforation_diameter
    dw = wellbore_diameter
    spf = shots_per_foot
    lp = penetration_depth
    alpha = math.radians(phasing_angle)
    
    # Karakas and Tariq correlation
    rw = dw / 2
    rp = dp / 2
    
    # Effective wellbore radius
    rwe = rw * (1 + 2 * lp / rw)**0.5
    
    # Flow efficiency
    fe = (rw / rwe) * (spf / 12) * math.sin(alpha / 2)
    
    return min(1.0, fe)


def skin_factor_perforation(
    perforation_diameter: float,
    wellbore_diameter: float,
    shots_per_foot: float,
    penetration_depth: float,
    damaged_zone_permeability: float,
    formation_permeability: float,
    damaged_zone_radius: float
) -> float:
    """
    Calculates skin factor due to perforation.
    
    Args:
        perforation_diameter (float): Perforation diameter in inches
        wellbore_diameter (float): Wellbore diameter in inches
        shots_per_foot (float): Number of shots per foot
        penetration_depth (float): Penetration depth in inches
        damaged_zone_permeability (float): Permeability in damaged zone in md
        formation_permeability (float): Formation permeability in md
        damaged_zone_radius (float): Damaged zone radius in inches
        
    Returns:
        float: Perforation skin factor (dimensionless)
    """
    dp = perforation_diameter / 2  # radius in inches
    rw = wellbore_diameter / 2
    spf = shots_per_foot
    lp = penetration_depth
    kd = damaged_zone_permeability
    k = formation_permeability
    rd = damaged_zone_radius
    
    # Convert to consistent units (ft)
    rw_ft = rw / 12
    dp_ft = dp / 12
    lp_ft = lp / 12
    rd_ft = rd / 12
    
    # Karakas and Tariq model
    rwD = rw_ft / lp_ft
    a = 2 / (spf / 12)  # perforation spacing
    
    # Skin components
    s_perf = math.log(a / (2 * dp_ft))
    s_damage = (k / kd - 1) * math.log(rd_ft / rw_ft)
    
    total_skin = s_perf + s_damage
    
    return total_skin


def fracture_half_length_pkn(
    injection_rate: float,
    injection_time: float,
    fluid_viscosity: float,
    formation_height: float,
    young_modulus: float,
    poisson_ratio: float,
    fracture_toughness: float = 1000
) -> float:
    """
    Calculates fracture half-length using PKN model.
    
    Args:
        injection_rate (float): Injection rate in bbl/min
        injection_time (float): Injection time in minutes
        fluid_viscosity (float): Fracturing fluid viscosity in cp
        formation_height (float): Net pay height in ft
        young_modulus (float): Young's modulus in psi
        poisson_ratio (float): Poisson's ratio (dimensionless)
        fracture_toughness (float): Fracture toughness in psi√in
        
    Returns:
        float: Fracture half-length in ft
    """
    q = injection_rate * 5.615  # Convert to ft³/min
    t = injection_time
    mu = fluid_viscosity
    h = formation_height
    e = young_modulus
    nu = poisson_ratio
    kic = fracture_toughness
    
    # Plane strain modulus
    ep = e / (1 - nu**2)
    
    # PKN model
    xf = 0.52 * (q**0.8 * mu**0.2 * t**0.8 * ep**0.2) / (h**0.2 * kic**0.4)
    
    return xf


def fracture_width_pkn(
    injection_rate: float,
    fluid_viscosity: float,
    formation_height: float,
    young_modulus: float,
    poisson_ratio: float,
    fracture_half_length: float
) -> float:
    """
    Calculates fracture width using PKN model.
    
    Args:
        injection_rate (float): Injection rate in bbl/min
        fluid_viscosity (float): Fracturing fluid viscosity in cp
        formation_height (float): Net pay height in ft
        young_modulus (float): Young's modulus in psi
        poisson_ratio (float): Poisson's ratio (dimensionless)
        fracture_half_length (float): Fracture half-length in ft
        
    Returns:
        float: Fracture width in inches
    """
    q = injection_rate * 5.615  # Convert to ft³/min
    mu = fluid_viscosity
    h = formation_height
    e = young_modulus
    nu = poisson_ratio
    xf = fracture_half_length
    
    # Plane strain modulus
    ep = e / (1 - nu**2)
    
    # PKN model
    w = 2.5 * (q * mu / ep)**(1/4) * (xf / h)**(1/4)
    
    return w * 12  # Convert to inches


def proppant_concentration(
    proppant_mass: float,
    fracture_volume: float
) -> float:
    """
    Calculates proppant concentration in fracture.
    
    Args:
        proppant_mass (float): Total proppant mass in lbs
        fracture_volume (float): Fracture volume in ft³
        
    Returns:
        float: Proppant concentration in lbs/ft³
    """
    if fracture_volume <= 0:
        raise ValueError("Fracture volume must be positive")
    
    return proppant_mass / fracture_volume


def fracture_conductivity(
    proppant_permeability: float,
    propped_width: float
) -> float:
    """
    Calculates fracture conductivity.
    
    Args:
        proppant_permeability (float): Proppant permeability in md
        propped_width (float): Propped fracture width in inches
        
    Returns:
        float: Fracture conductivity in md-ft
    """
    kf = proppant_permeability
    wf = propped_width / 12  # Convert to ft
    
    fc = kf * wf
    return fc


def dimensionless_fracture_conductivity(
    fracture_conductivity: float,
    formation_permeability: float,
    fracture_half_length: float
) -> float:
    """
    Calculates dimensionless fracture conductivity.
    
    Args:
        fracture_conductivity (float): Fracture conductivity in md-ft
        formation_permeability (float): Formation permeability in md
        fracture_half_length (float): Fracture half-length in ft
        
    Returns:
        float: Dimensionless fracture conductivity
    """
    fc = fracture_conductivity
    k = formation_permeability
    xf = fracture_half_length
    
    cfd = fc / (k * xf)
    return cfd


def acid_penetration_distance(
    injection_rate: float,
    acid_concentration: float,
    formation_porosity: float,
    rock_dissolving_power: float,
    reaction_rate: float,
    injection_time: float
) -> float:
    """
    Calculates acid penetration distance in matrix acidizing.
    
    Args:
        injection_rate (float): Acid injection rate in bbl/min
        acid_concentration (float): Acid concentration in fraction
        formation_porosity (float): Formation porosity in fraction
        rock_dissolving_power (float): Rock dissolving power in lb rock/gal acid
        reaction_rate (float): Acid-rock reaction rate in 1/min
        injection_time (float): Injection time in minutes
        
    Returns:
        float: Acid penetration distance in ft
    """
    q = injection_rate
    c = acid_concentration
    phi = formation_porosity
    alpha = rock_dissolving_power
    k_rxn = reaction_rate
    t = injection_time
    
    # Simplified penetration model
    penetration = math.sqrt((q * c * t) / (phi * alpha * k_rxn)) / 10
    
    return penetration


def wormhole_velocity(
    injection_rate: float,
    wellbore_radius: float,
    formation_porosity: float,
    acid_efficiency: float = 0.1
) -> float:
    """
    Calculates wormhole propagation velocity in carbonate acidizing.
    
    Args:
        injection_rate (float): Acid injection rate in bbl/min
        wellbore_radius (float): Wellbore radius in ft
        formation_porosity (float): Formation porosity in fraction
        acid_efficiency (float): Acid utilization efficiency (default 0.1)
        
    Returns:
        float: Wormhole velocity in ft/min
    """
    q = injection_rate * 5.615  # Convert to ft³/min
    rw = wellbore_radius
    phi = formation_porosity
    eta = acid_efficiency
    
    # Simplified wormhole model
    area = 2 * math.pi * rw  # Approximate contact area
    velocity = (q * eta) / (area * phi)
    
    return velocity


def sand_control_gravel_size(
    formation_sand_d50: float,
    formation_sand_uc: float = 5.0
) -> float:
    """
    Calculates optimal gravel size for sand control.
    
    Args:
        formation_sand_d50 (float): Formation sand median size in mesh
        formation_sand_uc (float): Formation sand uniformity coefficient (default 5.0)
        
    Returns:
        float: Recommended gravel size in mesh
    """
    d50 = formation_sand_d50
    uc = formation_sand_uc
    
    # Saucier criterion
    if uc < 3:
        # Well sorted sand
        gravel_size = 6 * d50
    elif uc < 10:
        # Moderately sorted sand
        gravel_size = 5 * d50
    else:
        # Poorly sorted sand
        gravel_size = 4 * d50
    
    return gravel_size


def screen_slot_size(formation_sand_d10: float) -> float:
    """
    Calculates screen slot size for sand control.
    
    Args:
        formation_sand_d10 (float): Formation sand 10% passing size in mesh
        
    Returns:
        float: Recommended slot size in inches
    """
    d10 = formation_sand_d10
    
    # Conservative approach: slot size = 1.5 × D10
    slot_size = 1.5 * d10
    
    # Convert mesh to inches (approximate)
    slot_inches = 0.0029 * slot_size
    
    return slot_inches


def acid_penetration_distance(
    average_fracture_width: float,
    dimensionless_acid_penetration: float,
    reynolds_number: float,
    reynolds_number_fluid_loss: float
) -> float:
    """
    Calculates acid penetration distance in acidizing operations.
    
    Args:
        average_fracture_width (float): Average fracture width (ft)
        dimensionless_acid_penetration (float): Dimensionless acid penetration distance (dimensionless)
        reynolds_number (float): Reynolds number (dimensionless)
        reynolds_number_fluid_loss (float): Reynolds number for fluid loss (dimensionless)
        
    Returns:
        float: Acid penetration distance (ft)
        
    Reference:
        Chapter 4, Formula 4.1
    """
    return average_fracture_width * dimensionless_acid_penetration


def fracture_gradient_calculation(
    depth: float,
    overburden_gradient: float = 1.0,
    pore_pressure_gradient: float = 0.433,
    poisson_ratio: float = 0.25
) -> float:
    """
    Calculates fracture gradient for hydraulic fracturing.
    
    Args:
        depth (float): Depth (ft)
        overburden_gradient (float): Overburden gradient (psi/ft), default 1.0
        pore_pressure_gradient (float): Pore pressure gradient (psi/ft), default 0.433
        poisson_ratio (float): Poisson's ratio (dimensionless), default 0.25
        
    Returns:
        float: Fracture gradient (psi/ft)
        
    Reference:
        Chapter 4, Formula 4.38
    """
    stress_ratio = poisson_ratio / (1 - poisson_ratio)
    minimum_horizontal_stress = (stress_ratio * 
                                (overburden_gradient - pore_pressure_gradient) * depth + 
                                pore_pressure_gradient * depth)
    
    return minimum_horizontal_stress / depth


def hydraulic_fracture_efficiency(
    injected_volume: float,
    fracture_volume: float
) -> float:
    """
    Calculates hydraulic fracture efficiency.
    
    Args:
        injected_volume (float): Total injected volume (bbl)
        fracture_volume (float): Created fracture volume (bbl)
        
    Returns:
        float: Fracture efficiency (fraction)
        
    Reference:
        Chapter 4, Formula 4.42
    """
    return fracture_volume / injected_volume


def fracture_conductivity_calculation(
    fracture_permeability: float,
    fracture_width: float
) -> float:
    """
    Calculates fracture conductivity.
    
    Args:
        fracture_permeability (float): Fracture permeability (mD)
        fracture_width (float): Fracture width (ft)
        
    Returns:
        float: Fracture conductivity (mD·ft)
        
    Reference:
        Chapter 4, Formula 4.34
    """
    return fracture_permeability * fracture_width


def equivalent_skin_factor_fractured_wells(
    formation_permeability: float,
    fracture_conductivity: float,
    fracture_half_length: float,
    wellbore_radius: float
) -> float:
    """
    Calculates equivalent skin factor in fractured wells.
    
    Args:
        formation_permeability (float): Formation permeability (mD)
        fracture_conductivity (float): Fracture conductivity (mD·ft)
        fracture_half_length (float): Fracture half length (ft)
        wellbore_radius (float): Wellbore radius (ft)
        
    Returns:
        float: Equivalent skin factor (dimensionless)
        
    Reference:
        Chapter 4, Formula 4.27
    """
    import math
    
    conductivity_ratio = fracture_conductivity / (formation_permeability * fracture_half_length)
    
    if conductivity_ratio > 100:  # Infinite conductivity
        return math.log(fracture_half_length / wellbore_radius) - 0.5
    else:  # Finite conductivity
        return math.log(fracture_half_length / wellbore_radius) - 0.5 + (1 / (2 * conductivity_ratio))


def perforation_skin_factor_calculation(
    wellbore_radius: float,
    perforation_length: float,
    perforation_diameter: float,
    shots_per_foot: float,
    phasing_angle: float,
    formation_permeability: float,
    damaged_zone_permeability: float,
    damaged_zone_radius: float
) -> float:
    """
    Calculates perforation skin factor.
    
    Args:
        wellbore_radius (float): Wellbore radius (ft)
        perforation_length (float): Perforation length (ft)
        perforation_diameter (float): Perforation diameter (ft)
        shots_per_foot (float): Shots per foot
        phasing_angle (float): Phasing angle (degrees)
        formation_permeability (float): Formation permeability (mD)
        damaged_zone_permeability (float): Damaged zone permeability (mD)
        damaged_zone_radius (float): Damaged zone radius (ft)
        
    Returns:
        float: Perforation skin factor (dimensionless)
        
    Reference:
        Chapter 4, Formula 4.60
    """
    import math
    
    # Convert phasing angle to radians
    alpha = math.radians(phasing_angle)
    
    # Effective wellbore radius
    effective_radius = wellbore_radius * (1 + 2 * perforation_length / wellbore_radius)**0.5
    
    # Perforation density effect
    density_factor = (4 / shots_per_foot) * math.sin(alpha / 2)
    
    # Skin components
    geometric_skin = math.log(effective_radius / wellbore_radius)
    damage_skin = (formation_permeability / damaged_zone_permeability - 1) * math.log(damaged_zone_radius / wellbore_radius)
    perforation_skin = math.log(density_factor / perforation_diameter)
    
    return geometric_skin + damage_skin + perforation_skin


def productivity_ratio_fractured_formation(
    productivity_index_fractured: float,
    productivity_index_unfractured: float
) -> float:
    """
    Calculates productivity ratio of a hydraulically fractured formation.
    
    Args:
        productivity_index_fractured (float): Productivity index after fracturing (STB/day/psi)
        productivity_index_unfractured (float): Productivity index before fracturing (STB/day/psi)
        
    Returns:
        float: Productivity ratio (dimensionless)
        
    Reference:
        Chapter 4, Formula 4.69
    """
    return productivity_index_fractured / productivity_index_unfractured


def choke_flow_rate_gas_sonic(
    upstream_pressure: float,
    upstream_temperature: float,
    choke_diameter: float,
    gas_specific_gravity: float,
    discharge_coefficient: float = 0.85
) -> float:
    """
    Calculates gas flow rate through choke under sonic conditions.
    
    Args:
        upstream_pressure (float): Upstream pressure (psia)
        upstream_temperature (float): Upstream temperature (°R)
        choke_diameter (float): Choke diameter (in.)
        gas_specific_gravity (float): Gas specific gravity (air = 1.0)
        discharge_coefficient (float): Discharge coefficient (default 0.85)
        
    Returns:
        float: Gas flow rate (MSCF/day)
        
    Reference:
        Chapter 4, Formula 4.41
    """
    import math
    
    area = math.pi * (choke_diameter / 2)**2  # in²
    
    # Sonic flow rate equation
    flow_rate = (3.85 * discharge_coefficient * area * upstream_pressure) / \
                math.sqrt(gas_specific_gravity * upstream_temperature)
    
    return flow_rate * 24  # Convert to daily rate


def perforation_pressure_drop_oil_wells(
    oil_flow_rate: float,
    oil_viscosity: float,
    perforation_diameter: float,
    shots_per_foot: float,
    perforation_length: float
) -> float:
    """
    Calculates pressure drop across perforations in oil wells.
    
    Args:
        oil_flow_rate (float): Oil flow rate (STB/day)
        oil_viscosity (float): Oil viscosity (cp)
        perforation_diameter (float): Perforation diameter (in.)
        shots_per_foot (float): Shots per foot
        perforation_length (float): Perforation length (in.)
        
    Returns:
        float: Pressure drop across perforations (psi)
        
    Reference:
        Chapter 4, Formula 4.63
    """
    # Convert units
    flow_rate_bpd = oil_flow_rate
    area_per_shot = math.pi * (perforation_diameter / 2)**2  # in²
    total_area = area_per_shot * shots_per_foot  # in²/ft
    
    # Pressure drop calculation
    pressure_drop = (0.5 * oil_viscosity * flow_rate_bpd) / \
                   (total_area * perforation_length)
    
    return pressure_drop


def fracture_area_hydraulically_fractured(
    fracture_half_length: float,
    fracture_height: float
) -> float:
    """
    Calculates fracture area of a hydraulically fractured formation.
    
    Args:
        fracture_half_length (float): Fracture half length (ft)
        fracture_height (float): Fracture height (ft)
        
    Returns:
        float: Fracture area (ft²)
        
    Reference:
        Chapter 4, Formula 4.33
    """
    return 2 * fracture_half_length * fracture_height


def injection_pressure_hydraulic_fracturing(
    minimum_horizontal_stress: float,
    net_pressure: float,
    friction_pressure: float,
    hydrostatic_pressure: float
) -> float:
    """
    Calculates injection pressure for hydraulic fracturing.
    
    Args:
        minimum_horizontal_stress (float): Minimum horizontal stress (psi)
        net_pressure (float): Net pressure (psi)
        friction_pressure (float): Friction pressure (psi)
        hydrostatic_pressure (float): Hydrostatic pressure (psi)
        
    Returns:
        float: Injection pressure (psi)
        
    Reference:
        Chapter 4, Formula 4.47
    """
    return minimum_horizontal_stress + net_pressure + friction_pressure - hydrostatic_pressure
