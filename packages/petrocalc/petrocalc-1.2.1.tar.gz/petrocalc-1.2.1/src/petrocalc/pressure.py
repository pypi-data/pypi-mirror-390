"""
Pressure calculations and analysis.

This module contains functions for pressure-related calculations including:
- Hydrostatic and formation pressures
- Pressure gradient calculations
- Well control calculations
- Kick analysis and well control
- Advanced pressure correlations
"""

import math
from typing import Union, Tuple, Optional


def formation_pressure_gradient(
    formation_water_density: float,
    salinity: float = 100000,
    temperature: float = 150
) -> float:
    """
    Calculates formation pressure gradient.
    
    Args:
        formation_water_density (float): Formation water density in lb/ft³
        salinity (float): Water salinity in ppm (default 100,000)
        temperature (float): Formation temperature in °F (default 150)
        
    Returns:
        float: Formation pressure gradient in psi/ft
    """
    rho_w = formation_water_density
    
    # Convert density to pressure gradient
    pressure_gradient = rho_w / 144  # psi/ft
    
    return pressure_gradient


def overburden_pressure_gradient(depth: float, surface_density: float = 18.0) -> float:
    """
    Calculates overburden pressure gradient.
    
    Args:
        depth (float): Depth in ft
        surface_density (float): Average surface density in lb/ft³ (default 18.0)
        
    Returns:
        float: Overburden pressure gradient in psi/ft
    """
    # Typical overburden gradient increases with depth
    if depth < 1000:
        gradient = 0.8 + 0.15 * (depth / 1000)
    else:
        gradient = 0.95 + 0.05 * ((depth - 1000) / 9000)
    
    return min(1.1, gradient)  # Cap at 1.1 psi/ft


def fracture_pressure_gradient(
    overburden_gradient: float,
    pore_pressure_gradient: float,
    poisson_ratio: float = 0.25
) -> float:
    """
    Calculates fracture pressure gradient using Eaton's method.
    
    Args:
        overburden_gradient (float): Overburden pressure gradient in psi/ft
        pore_pressure_gradient (float): Pore pressure gradient in psi/ft
        poisson_ratio (float): Poisson's ratio (default 0.25)
        
    Returns:
        float: Fracture pressure gradient in psi/ft
    """
    s_ob = overburden_gradient
    s_pp = pore_pressure_gradient
    nu = poisson_ratio
    
    # Eaton's correlation
    k = nu / (1 - nu)
    fracture_gradient = k * (s_ob - s_pp) + s_pp
    
    return fracture_gradient


def equivalent_mud_weight(pressure: float, depth: float) -> float:
    """
    Calculates equivalent mud weight from pressure and depth.
    
    Args:
        pressure (float): Pressure in psi
        depth (float): Depth in ft
        
    Returns:
        float: Equivalent mud weight in ppg
    """
    if depth <= 0:
        raise ValueError("Depth must be positive")
    
    emw = pressure / (0.052 * depth)
    return emw


def kick_tolerance(
    casing_shoe_depth: float,
    formation_pressure: float,
    fracture_pressure: float,
    current_mud_weight: float
) -> float:
    """
    Calculates kick tolerance for well control.
    
    Args:
        casing_shoe_depth (float): Casing shoe depth in ft
        formation_pressure (float): Formation pressure in psi
        fracture_pressure (float): Fracture pressure at shoe in psi
        current_mud_weight (float): Current mud weight in ppg
        
    Returns:
        float: Kick tolerance in ppg equivalent
    """
    d_shoe = casing_shoe_depth
    p_form = formation_pressure
    p_frac = fracture_pressure
    mw_current = current_mud_weight
    
    # Maximum allowable surface pressure
    p_max_surface = p_frac - (mw_current * 0.052 * d_shoe)
    
    # Kick tolerance
    kt = p_max_surface / (0.052 * d_shoe)
    
    return kt


def kill_mud_weight(
    original_mud_weight: float,
    shut_in_drillpipe_pressure: float,
    true_vertical_depth: float
) -> float:
    """
    Calculates kill mud weight for well control.
    
    Args:
        original_mud_weight (float): Original mud weight in ppg
        shut_in_drillpipe_pressure (float): SIDPP in psi
        true_vertical_depth (float): True vertical depth in ft
        
    Returns:
        float: Kill mud weight in ppg
    """
    mw_orig = original_mud_weight
    sidpp = shut_in_drillpipe_pressure
    tvd = true_vertical_depth
    
    if tvd <= 0:
        raise ValueError("True vertical depth must be positive")
    
    # Kill mud weight calculation
    kmw = mw_orig + (sidpp / (0.052 * tvd))
    
    return kmw


def initial_circulating_pressure(
    shut_in_drillpipe_pressure: float,
    slow_pump_rate_pressure: float
) -> float:
    """
    Calculates initial circulating pressure for well control.
    
    Args:
        shut_in_drillpipe_pressure (float): SIDPP in psi
        slow_pump_rate_pressure (float): Slow pump rate pressure in psi
        
    Returns:
        float: Initial circulating pressure in psi
    """
    sidpp = shut_in_drillpipe_pressure
    spr = slow_pump_rate_pressure
    
    icp = sidpp + spr
    return icp


def final_circulating_pressure(
    slow_pump_rate_pressure: float,
    original_mud_weight: float,
    kill_mud_weight: float
) -> float:
    """
    Calculates final circulating pressure for well control.
    
    Args:
        slow_pump_rate_pressure (float): Slow pump rate pressure in psi
        original_mud_weight (float): Original mud weight in ppg
        kill_mud_weight (float): Kill mud weight in ppg
        
    Returns:
        float: Final circulating pressure in psi
    """
    spr = slow_pump_rate_pressure
    mw_orig = original_mud_weight
    mw_kill = kill_mud_weight
    
    if mw_orig <= 0:
        raise ValueError("Original mud weight must be positive")
    
    fcp = spr * (mw_kill / mw_orig)**2
    return fcp


def maximum_allowable_annular_surface_pressure(
    fracture_pressure: float,
    mud_weight: float,
    shoe_depth: float
) -> float:
    """
    Calculates maximum allowable annular surface pressure.
    
    Args:
        fracture_pressure (float): Fracture pressure at shoe in psi
        mud_weight (float): Current mud weight in ppg
        shoe_depth (float): Shoe depth in ft
        
    Returns:
        float: MAASP in psi
    """
    p_frac = fracture_pressure
    mw = mud_weight
    d_shoe = shoe_depth
    
    # Hydrostatic pressure at shoe
    p_hydro = mw * 0.052 * d_shoe
    
    # MAASP
    maasp = p_frac - p_hydro
    
    return max(0, maasp)


def pit_gain_calculation(
    kick_volume: float,
    formation_gas_gradient: float = 0.1,
    mud_gradient: float = 0.45
) -> float:
    """
    Calculates pit gain during gas kick migration.
    
    Args:
        kick_volume (float): Original kick volume in bbls
        formation_gas_gradient (float): Gas gradient in psi/ft (default 0.1)
        mud_gradient (float): Mud gradient in psi/ft (default 0.45)
        
    Returns:
        float: Expected pit gain in bbls
    """
    v_kick = kick_volume
    grad_gas = formation_gas_gradient
    grad_mud = mud_gradient
    
    # Gas expansion factor (simplified)
    expansion_factor = grad_mud / grad_gas
    
    # Pit gain
    pit_gain = v_kick * (expansion_factor - 1)
    
    return pit_gain


def pump_pressure_schedule(
    initial_circulating_pressure: float,
    final_circulating_pressure: float,
    total_pump_strokes: float,
    current_stroke: float
) -> float:
    """
    Calculates pump pressure for kill operation.
    
    Args:
        initial_circulating_pressure (float): ICP in psi
        final_circulating_pressure (float): FCP in psi
        total_pump_strokes (float): Total pump strokes to circulate
        current_stroke (float): Current pump stroke number
        
    Returns:
        float: Required pump pressure in psi
    """
    icp = initial_circulating_pressure
    fcp = final_circulating_pressure
    total_strokes = total_pump_strokes
    current = current_stroke
    
    if total_strokes <= 0:
        raise ValueError("Total pump strokes must be positive")
    
    # Linear pressure reduction
    pressure = icp - (icp - fcp) * (current / total_strokes)
    
    return pressure


def lost_circulation_pressure(
    formation_pressure: float,
    hydrostatic_pressure: float,
    safety_margin: float = 50
) -> float:
    """
    Calculates pressure at which lost circulation may occur.
    
    Args:
        formation_pressure (float): Formation pressure in psi
        hydrostatic_pressure (float): Hydrostatic pressure in psi
        safety_margin (float): Safety margin in psi (default 50)
        
    Returns:
        float: Lost circulation pressure in psi
    """
    p_form = formation_pressure
    p_hydro = hydrostatic_pressure
    margin = safety_margin
    
    # Lost circulation occurs when pressure exceeds formation strength
    lc_pressure = p_form + margin
    
    return lc_pressure


def hydrostatic_pressure_detailed(
    mud_weight: float,
    depth: float,
    mud_weight_units: str = "ppg"
) -> float:
    """
    Calculates hydrostatic pressure with detailed mud weight handling.
    
    Args:
        mud_weight (float): Mud weight 
        depth (float): Depth (ft)
        mud_weight_units (str): Units for mud weight ("ppg", "lb/ft3", "kg/m3")
        
    Returns:
        float: Hydrostatic pressure (psi)
    """
    if mud_weight_units.lower() == "ppg":
        pressure = 0.052 * mud_weight * depth
    elif mud_weight_units.lower() == "lb/ft3":
        pressure = (mud_weight / 144) * depth
    elif mud_weight_units.lower() == "kg/m3":
        # Convert kg/m3 to ppg first
        ppg = mud_weight * 0.00834
        pressure = 0.052 * ppg * depth
    else:
        raise ValueError("Unsupported mud weight units. Use 'ppg', 'lb/ft3', or 'kg/m3'")
    
    return pressure


def gas_hydrate_dissociation_pressure(
    temperature: float,
    gas_gravity: float = 0.65
) -> float:
    """
    Calculates gas hydrate dissociation pressure.
    
    Args:
        temperature (float): Temperature (°F)
        gas_gravity (float): Gas specific gravity (air = 1.0), default 0.65
        
    Returns:
        float: Hydrate dissociation pressure (psia)
        
    Reference:
        Katz correlation for hydrate formation
    """
    t = temperature
    sg = gas_gravity
    
    # Convert temperature to absolute scale
    t_abs = t + 459.67  # °R
    
    # Katz correlation (simplified)
    log_p = 1.85 - 3100 / t_abs + 0.02 * sg
    p_hydrate = 10**log_p
    
    return max(0, p_hydrate)


def maximum_oil_column_height(
    oil_density: float,
    water_density: float,
    caprock_entry_pressure: float
) -> float:
    """
    Calculates maximum height of oil column that can be supported by caprock.
    
    Args:
        oil_density (float): Oil density (lb/ft³)
        water_density (float): Water density (lb/ft³)
        caprock_entry_pressure (float): Caprock entry pressure (psi)
        
    Returns:
        float: Maximum oil column height (ft)
        
    Reference:
        Reservoir engineering principles for hydrocarbon trapping
    """
    rho_o = oil_density
    rho_w = water_density
    pe = caprock_entry_pressure
    
    # Density difference
    delta_rho = rho_w - rho_o
    
    if delta_rho <= 0:
        return float('inf')  # No buoyancy contrast
    
    # Maximum column height
    h_max = pe * 144 / delta_rho  # Convert psi to lb/ft²
    
    return max(0, h_max)


def effective_compressibility_undersaturated(
    oil_compressibility: float,
    water_compressibility: float,
    rock_compressibility: float,
    water_saturation: float
) -> float:
    """
    Calculates effective compressibility in undersaturated oil reservoirs using Hawkins method.
    
    Args:
        oil_compressibility (float): Oil compressibility (1/psi)
        water_compressibility (float): Water compressibility (1/psi)
        rock_compressibility (float): Rock compressibility (1/psi)
        water_saturation (float): Water saturation (fraction)
        
    Returns:
        float: Effective compressibility (1/psi)
        
    Reference:
        Hawkins method for effective compressibility
    """
    co = oil_compressibility
    cw = water_compressibility
    cf = rock_compressibility
    sw = water_saturation
    so = 1 - sw  # Oil saturation
    
    # Hawkins correlation
    ce = so * co + sw * cw + cf
    
    return ce


def effective_compressibility_fetkovich(
    initial_water_saturation: float,
    water_compressibility: float,
    formation_compressibility: float,
    volume_ratio: float
) -> float:
    """
    Calculates cumulative effective compressibility using Fetkovich method.
    
    Args:
        initial_water_saturation (float): Initial water saturation (fraction)
        water_compressibility (float): Water compressibility (1/psi)
        formation_compressibility (float): Formation compressibility (1/psi)
        volume_ratio (float): Dimensionless volume ratio (dimensionless)
        
    Returns:
        float: Effective compressibility (1/psi)
        
    Reference:
        Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
        Gulf Publishing of Elsevier, Chapter: 3, Page: 215,216.
    """
    swi = initial_water_saturation
    cw = water_compressibility
    cf = formation_compressibility
    m = volume_ratio
    
    # Fetkovich correlation
    numerator = swi * cw + m * (cf + cw) + cf
    denominator = 1 - swi
    
    ce = numerator / denominator
    
    return ce


def geothermal_gradient_calculation(
    surface_temperature: float,
    bottom_hole_temperature: float,
    depth: float
) -> float:
    """
    Calculates geothermal gradient from temperature measurements.
    
    Args:
        surface_temperature (float): Surface temperature (°F)
        bottom_hole_temperature (float): Bottom hole temperature (°F)
        depth (float): Total depth (ft)
        
    Returns:
        float: Geothermal gradient (°F/ft)
        
    Reference:
        Standard geothermal calculations
    """
    if depth <= 0:
        raise ValueError("Depth must be positive")
    
    temp_diff = bottom_hole_temperature - surface_temperature
    gradient = temp_diff / depth
    
    return gradient


def formation_temperature_with_gradient(
    surface_temperature: float,
    depth: float,
    geothermal_gradient: float
) -> float:
    """
    Calculates formation temperature for a given depth and gradient.
    
    Args:
        surface_temperature (float): Surface temperature (°F)
        depth (float): Depth (ft)
        geothermal_gradient (float): Geothermal gradient (°F/ft)
        
    Returns:
        float: Formation temperature (°F)
        
    Reference:
        Standard petroleum engineering practice
    """
    return surface_temperature + (depth * geothermal_gradient)


def pressure_drawdown_analysis(
    initial_pressure: float,
    flow_rate: float,
    permeability: float,
    thickness: float,
    viscosity: float,
    formation_volume_factor: float,
    wellbore_radius: float,
    drainage_radius: float,
    time: float
) -> float:
    """
    Calculates pressure drawdown using radial flow equation.
    
    Args:
        initial_pressure (float): Initial reservoir pressure (psi)
        flow_rate (float): Flow rate (STB/day)
        permeability (float): Permeability (mD)
        thickness (float): Net pay thickness (ft)
        viscosity (float): Fluid viscosity (cP)
        formation_volume_factor (float): Formation volume factor (bbl/STB)
        wellbore_radius (float): Wellbore radius (ft)
        drainage_radius (float): Drainage radius (ft)
        time (float): Time since start of production (hours)
        
    Returns:
        float: Bottom hole flowing pressure (psi)
    """
    pi = initial_pressure
    q = flow_rate
    k = permeability
    h = thickness
    mu = viscosity
    b = formation_volume_factor
    rw = wellbore_radius
    re = drainage_radius
    t = time
    
    # Productivity index (steady state)
    j = (7.08 * k * h) / (mu * b * math.log(re / rw))
    
    # Pressure drawdown
    drawdown = q / j
    
    # Bottom hole flowing pressure
    pwf = pi - drawdown
    
    return max(0, pwf)


def critical_pressure_ratio(
    gamma: float = 1.4
) -> float:
    """
    Calculates critical pressure ratio for choked flow.
    
    Args:
        gamma (float): Heat capacity ratio (Cp/Cv), default 1.4 for ideal gas
        
    Returns:
        float: Critical pressure ratio (dimensionless)
        
    Reference:
        Gas dynamics for choked flow conditions
    """
    # Critical pressure ratio
    pr_crit = (2 / (gamma + 1))**(gamma / (gamma - 1))
    
    return pr_crit
