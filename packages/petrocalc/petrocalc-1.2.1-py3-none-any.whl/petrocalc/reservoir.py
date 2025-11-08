"""
Reservoir engineering calculations.

This module contains functions for reservoir engineering calculations including:
- Reservoir fluid properties
- Material balance equations
- Recovery calculations
- Decline curve analysis
- Well performance
- Permeability averaging methods
- API gravity calculations
"""

import math
from typing import Union, Tuple, Optional, List


def api_gravity_from_specific_gravity(specific_gravity: float) -> float:
    """
    Calculates API gravity from oil specific gravity.
    
    Args:
        specific_gravity (float): Specific gravity of oil phase (dimensionless)
        
    Returns:
        float: API gravity (degrees API)
        
    Notes:
        Specific gravity is oil density / water density at 60°F
        
    Reference:
        Wikipedia.org
    """
    return 141.5 / specific_gravity - 131.5


def specific_gravity_from_api(api_gravity: float) -> float:
    """
    Calculates specific gravity from API gravity.
    
    Args:
        api_gravity (float): API gravity (degrees API)
        
    Returns:
        float: Specific gravity of oil (dimensionless)
    """
    return 141.5 / (api_gravity + 131.5)


def average_permeability_layered_beds(
    permeabilities: List[float], 
    areas: List[float]
) -> float:
    """
    Calculates average permeability for linear flow in layered beds with no crossflow.
    
    Args:
        permeabilities (List[float]): Permeability for each layer (mD)
        areas (List[float]): Area of each layer (ft²)
        
    Returns:
        float: Average permeability (mD)
        
    Reference:
        Ahmed, T. (2006). Reservoir Engineering Handbook. Elsevier, Page: 238.
    """
    if len(permeabilities) != len(areas):
        raise ValueError("Number of permeabilities must equal number of areas")
    
    weighted_sum = sum(k * a for k, a in zip(permeabilities, areas))
    total_area = sum(areas)
    
    return weighted_sum / total_area


def average_permeability_series_beds(
    permeabilities: List[float], 
    lengths: List[float]
) -> float:
    """
    Calculates average permeability for linear flow in series beds.
    
    Args:
        permeabilities (List[float]): Permeability for each layer (mD)
        lengths (List[float]): Length of each layer (ft)
        
    Returns:
        float: Average permeability for series system (mD)
        
    Reference:
        Ahmed, T. (2006). Reservoir Engineering Handbook. Elsevier, Page: 240.
    """
    if len(permeabilities) != len(lengths):
        raise ValueError("Number of permeabilities must equal number of lengths")
    
    total_length = sum(lengths)
    harmonic_sum = sum(l / k for l, k in zip(lengths, permeabilities))
    
    return total_length / harmonic_sum


def average_permeability_parallel_layers(
    permeabilities: List[float], 
    heights: List[float]
) -> float:
    """
    Calculates average permeability for parallel-layered systems.
    
    Args:
        permeabilities (List[float]): Permeability for each layer (mD)
        heights (List[float]): Height of each layer (ft)
        
    Returns:
        float: Average permeability for parallel-layered systems (mD)
        
    Reference:
        Ahmed, T. (2006). Reservoir Engineering Handbook. Elsevier, Page: 237.
    """
    if len(permeabilities) != len(heights):
        raise ValueError("Number of permeabilities must equal number of heights")
    
    weighted_sum = sum(k * h for k, h in zip(permeabilities, heights))
    total_height = sum(heights)
    
    return weighted_sum / total_height


def average_permeability_radial_system(
    k_inner: float,
    k_outer: float,
    r_outer: float,
    r_wellbore: float,
    r_interface: float
) -> float:
    """
    Calculates average permeability in radial systems.
    
    Args:
        k_inner (float): Permeability between wellbore and interface radius (mD)
        k_outer (float): Permeability between interface and outer radius (mD)
        r_outer (float): Drainage radius (ft)
        r_wellbore (float): Wellbore radius (ft)
        r_interface (float): Interface radius (ft)
        
    Returns:
        float: Average permeability in radial systems (mD)
        
    Reference:
        Applied Reservoir Engineering Vol. 1, Smith, Tracy & Farrar, Equation 7–7.
    """
    total_ln = math.log(r_outer / r_wellbore)
    inner_ln = math.log(r_outer / r_interface)
    outer_ln = math.log(r_interface / r_wellbore)
    
    return (k_inner * k_outer * total_ln) / (k_inner * inner_ln + k_outer * outer_ln)


def average_temperature_gas_column(
    tubing_head_temp: float,
    wellbore_temp: float
) -> float:
    """
    Calculates arithmetic average temperature of a gas column.
    
    Args:
        tubing_head_temp (float): Tubing head temperature (°R)
        wellbore_temp (float): Wellbore temperature (°R)
        
    Returns:
        float: Arithmetic average temperature (°R)
        
    Reference:
        Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
        Gulf Publishing of Elsevier, Chapter: 3, Page: 199.
    """
    return (tubing_head_temp + wellbore_temp) / 2


def fractional_flow_water(
    water_viscosity: float,
    oil_viscosity: float,
    relative_perm_water: float,
    relative_perm_oil: float
) -> float:
    """
    Calculates fraction of total flowing stream composed of water.
    
    Args:
        water_viscosity (float): Water viscosity (cP)
        oil_viscosity (float): Oil viscosity (cP)
        relative_perm_water (float): Relative permeability to water (dimensionless)
        relative_perm_oil (float): Relative permeability to oil (dimensionless)
        
    Returns:
        float: Fraction of total flowing stream composed of water (dimensionless)
        
    Reference:
        Craig Jr. F. F., 2004, the Reservoir Engineering Aspects of Waterflooding, 
        Vol. 3. Richardson, Texas: Monograph Series, SPE, Page: 112.
    """
    mobility_ratio = (water_viscosity * relative_perm_oil) / (relative_perm_water * oil_viscosity)
    return 1 / (1 + mobility_ratio)


def capillary_number(
    displacing_fluid_viscosity: float,
    characteristic_velocity: float,
    interfacial_tension: float
) -> float:
    """
    Calculates capillary number for displacement processes.
    
    Args:
        displacing_fluid_viscosity (float): Viscosity of displacing fluid (cP)
        characteristic_velocity (float): Characteristic velocity (ft/D)
        interfacial_tension (float): Surface/interfacial tension of oil and water phases (dyn/cm)
        
    Returns:
        float: Capillary number (dimensionless)
        
    Reference:
        Wikipedia.org
    """
    return (displacing_fluid_viscosity * characteristic_velocity) / interfacial_tension


def capillary_pressure(
    interfacial_tension: float,
    contact_angle: float,
    pore_radius: float
) -> float:
    """
    Calculates capillary pressure.
    
    Args:
        interfacial_tension (float): Fluid interfacial tension (dyn/cm)
        contact_angle (float): Contact angle of wettability (degrees)
        pore_radius (float): Radius of capillary (cm)
        
    Returns:
        float: Capillary pressure (dyn/cm²)
        
    Reference:
        Wikipedia.org
    """
    contact_angle_rad = math.radians(contact_angle)
    return (2 * interfacial_tension * math.cos(contact_angle_rad)) / pore_radius


def characteristic_diffusion_time(
    porosity: float,
    fluid_compressibility: float,
    rock_compressibility: float,
    viscosity: float,
    length_scale: float,
    permeability: float
) -> float:
    """
    Calculates characteristic time for linear diffusion in reservoirs.
    
    Args:
        porosity (float): Porosity (fraction)
        fluid_compressibility (float): Fluid compressibility (1/psi)
        rock_compressibility (float): Rock compressibility (1/psi)
        viscosity (float): Viscosity (cP)
        length_scale (float): Characteristic length scale of diffusion (ft)
        permeability (float): Permeability (mD)
        
    Returns:
        float: Characteristic diffusion time (seconds)
        
    Reference:
        Zoback, M. D. Reservoir Geomechanics, Cambridge University Express, UK, Page: 41.
    """
    total_compressibility = fluid_compressibility + rock_compressibility
    return (porosity * total_compressibility * viscosity * length_scale**2) / permeability


def cumulative_oil_production_undersaturated(
    initial_oil_in_place: float,
    effective_compressibility: float,
    oil_fvf_current: float,
    oil_fvf_initial: float,
    pressure_drop: float
) -> float:
    """
    Calculates cumulative oil production for undersaturated oil reservoirs.
    
    Args:
        initial_oil_in_place (float): Initial oil-in-place (STB)
        effective_compressibility (float): Effective compressibility (1/psi)
        oil_fvf_current (float): Oil formation volume factor at current pressure (bbl/STB)
        oil_fvf_initial (float): Oil formation volume factor at initial pressure (bbl/STB)
        pressure_drop (float): Pressure differential (psi)
        
    Returns:
        float: Cumulative oil production (STB)
        
    Reference:
        Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
        Gulf Publishing of Elsevier, Chapter: 5, Page: 333.
    """
    return initial_oil_in_place * effective_compressibility * (oil_fvf_current / oil_fvf_initial) * pressure_drop


def formation_temperature_gradient(
    surface_temperature: float,
    depth: float,
    geothermal_gradient: float = 0.025
) -> float:
    """
    Calculates formation temperature for a given depth and gradient.
    
    Args:
        surface_temperature (float): Surface temperature (°F)
        depth (float): Depth (ft)
        geothermal_gradient (float): Geothermal gradient (°F/ft), default 0.025
        
    Returns:
        float: Formation temperature (°F)
        
    Reference:
        Standard petroleum engineering practice
    """
    return surface_temperature + (depth * geothermal_gradient)


def oil_formation_volume_factor_standing(
    gas_oil_ratio: float,
    gas_gravity: float, 
    oil_gravity: float,
    temperature: float,
    pressure: float
) -> float:
    """
    Calculates oil formation volume factor using Standing's correlation.
    
    Args:
        gas_oil_ratio (float): Solution gas-oil ratio in scf/STB
        gas_gravity (float): Gas specific gravity (air = 1.0)
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        
    Returns:
        float: Oil formation volume factor in res bbl/STB
    """
    rs = gas_oil_ratio
    gamma_g = gas_gravity
    gamma_o = 141.5 / (oil_gravity + 131.5)  # Convert API to specific gravity
    t = temperature
    p = pressure
    
    # Standing's correlation
    bob = 0.9759 + 0.000120 * (rs * (gamma_g / gamma_o)**0.5 + 1.25 * t)**1.2
    return bob


def gas_formation_volume_factor(temperature: float, pressure: float, z_factor: float = 1.0) -> float:
    """
    Calculates gas formation volume factor.
    
    Args:
        temperature (float): Temperature in °R (°F + 459.67)
        pressure (float): Pressure in psia
        z_factor (float): Gas compressibility factor (dimensionless)
        
    Returns:
        float: Gas formation volume factor in res ft³/scf
    """
    return 0.02827 * z_factor * temperature / pressure


def solution_gas_oil_ratio_standing(
    pressure: float,
    temperature: float,
    gas_gravity: float,
    oil_gravity: float
) -> float:
    """
    Calculates solution gas-oil ratio using Standing's correlation.
    
    Args:
        pressure (float): Pressure in psia
        temperature (float): Temperature in °F
        gas_gravity (float): Gas specific gravity (air = 1.0)
        oil_gravity (float): Oil API gravity in degrees
        
    Returns:
        float: Solution gas-oil ratio in scf/STB
    """
    gamma_g = gas_gravity
    api = oil_gravity
    t = temperature
    p = pressure
    
    # Standing's correlation
    rs = gamma_g * ((p / 18.2) + 1.4) * (10**(0.0125 * api - 0.00091 * t))
    return rs


def bubble_point_pressure_standing(
    gas_oil_ratio: float,
    gas_gravity: float,
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates bubble point pressure using Standing's correlation.
    
    Args:
        gas_oil_ratio (float): Solution gas-oil ratio in scf/STB
        gas_gravity (float): Gas specific gravity (air = 1.0)
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        
    Returns:
        float: Bubble point pressure in psia
    """
    rs = gas_oil_ratio
    gamma_g = gas_gravity
    api = oil_gravity
    t = temperature
    
    # Standing's correlation
    pb = 18.2 * ((rs / gamma_g)**0.83 * 10**(0.00091 * t - 0.0125 * api) - 1.4)
    return pb


def oil_viscosity_beggs_robinson(
    oil_gravity: float,
    temperature: float,
    pressure: float,
    gas_oil_ratio: float = 0
) -> float:
    """
    Calculates oil viscosity using Beggs-Robinson correlation.
    
    Args:
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        gas_oil_ratio (float): Solution gas-oil ratio in scf/STB
        
    Returns:
        float: Oil viscosity in cp
    """
    api = oil_gravity
    t = temperature
    rs = gas_oil_ratio
    
    # Dead oil viscosity
    x = t**(-1.163)
    y = 10**(3.0324 - 0.02023 * api) * x
    mu_od = 10**y - 1
    
    # Live oil viscosity
    if rs > 0:
        a = 10.715 * (rs + 100)**(-0.515)
        b = 5.44 * (rs + 150)**(-0.338)
        mu_o = a * mu_od**b
    else:
        mu_o = mu_od
    
    return mu_o


def gas_viscosity_lee(
    molecular_weight: float,
    temperature: float,
    pressure: float,
    specific_gravity: float
) -> float:
    """
    Calculates gas viscosity using Lee correlation.
    
    Args:
        molecular_weight (float): Gas molecular weight in lb/lb-mol
        temperature (float): Temperature in °R
        pressure (float): Pressure in psia
        specific_gravity (float): Gas specific gravity (air = 1.0)
        
    Returns:
        float: Gas viscosity in cp
    """
    mw = molecular_weight
    t = temperature
    p = pressure
    sg = specific_gravity
    
    # Gas density
    rho_g = (p * mw) / (10.732 * t)  # lb/ft³
    
    # Lee correlation
    k = ((9.379 + 0.01607 * mw) * t**1.5) / (209.2 + 19.26 * mw + t)
    x = 3.448 + (986.4 / t) + 0.01009 * mw
    y = 2.447 - 0.2224 * x
    
    mu_g = k * math.exp(x * (rho_g / 62.428)**y) / 10000
    return mu_g


def material_balance_oil_reservoir(
    initial_oil_in_place: float,
    cumulative_oil_production: float,
    cumulative_gas_production: float,
    cumulative_water_production: float,
    initial_formation_volume_factor: float,
    current_formation_volume_factor: float,
    initial_solution_gor: float,
    current_solution_gor: float,
    gas_formation_volume_factor: float
) -> float:
    """
    Calculates current reservoir pressure using material balance equation.
    
    Args:
        initial_oil_in_place (float): Initial oil in place in STB
        cumulative_oil_production (float): Cumulative oil production in STB
        cumulative_gas_production (float): Cumulative gas production in scf
        cumulative_water_production (float): Cumulative water production in STB
        initial_formation_volume_factor (float): Initial oil FVF in res bbl/STB
        current_formation_volume_factor (float): Current oil FVF in res bbl/STB
        initial_solution_gor (float): Initial solution GOR in scf/STB
        current_solution_gor (float): Current solution GOR in scf/STB
        gas_formation_volume_factor (float): Gas FVF in res ft³/scf
        
    Returns:
        float: Remaining oil in reservoir in STB
    """
    n = initial_oil_in_place
    np = cumulative_oil_production
    gp = cumulative_gas_production
    wp = cumulative_water_production
    boi = initial_formation_volume_factor
    bo = current_formation_volume_factor
    rsi = initial_solution_gor
    rs = current_solution_gor
    bg = gas_formation_volume_factor
    
    # Simplified material balance (no water influx, no gas cap)
    remaining_oil = n - np - (gp - np * rs) * (bg / 5.615) / (bo - rsi * bg / 5.615)
    return remaining_oil


def arps_decline_curve(
    initial_rate: float,
    time: float,
    decline_rate: float,
    decline_exponent: float = 1.0
) -> float:
    """
    Calculates production rate using Arps decline curve equation.
    
    Args:
        initial_rate (float): Initial production rate
        time (float): Time period
        decline_rate (float): Initial decline rate (1/time)
        decline_exponent (float): Decline exponent (b-factor)
        
    Returns:
        float: Production rate at given time
    """
    qi = initial_rate
    t = time
    di = decline_rate
    b = decline_exponent
    
    if b == 0:  # Exponential decline
        q = qi * math.exp(-di * t)
    else:  # Hyperbolic decline
        q = qi / (1 + b * di * t)**(1/b)
    
    return q


def cumulative_production_arps(
    initial_rate: float,
    time: float,
    decline_rate: float,
    decline_exponent: float = 1.0
) -> float:
    """
    Calculates cumulative production using Arps decline curve.
    
    Args:
        initial_rate (float): Initial production rate
        time (float): Time period
        decline_rate (float): Initial decline rate (1/time)
        decline_exponent (float): Decline exponent (b-factor)
        
    Returns:
        float: Cumulative production at given time
    """
    qi = initial_rate
    t = time
    di = decline_rate
    b = decline_exponent
    
    if abs(b) < 1e-6:  # Exponential decline (b ≈ 0)
        if di == 0:
            qcum = qi * t  # Constant rate
        else:
            qcum = (qi / di) * (1 - math.exp(-di * t))
    elif abs(b - 1.0) < 1e-6:  # Harmonic decline (b = 1)
        qcum = (qi / di) * math.log(1 + di * t)
    else:  # Hyperbolic decline
        if di == 0:
            qcum = qi * t  # Constant rate
        else:
            qcum = (qi / ((1 - b) * di)) * (1 - (1 + b * di * t)**(1 - 1/b))
    
    return qcum


def recovery_factor_waterflooding(
    initial_water_saturation: float,
    residual_oil_saturation: float,
    porosity: float,
    sweep_efficiency: float
) -> float:
    """
    Calculates oil recovery factor for waterflooding.
    
    Args:
        initial_water_saturation (float): Initial water saturation (fraction)
        residual_oil_saturation (float): Residual oil saturation (fraction)
        porosity (float): Porosity (fraction)
        sweep_efficiency (float): Sweep efficiency (fraction)
        
    Returns:
        float: Recovery factor (fraction)
    """
    swi = initial_water_saturation
    sor = residual_oil_saturation
    phi = porosity
    es = sweep_efficiency
    
    # Volumetric sweep efficiency
    ed = 1 - swi - sor  # Displacement efficiency
    recovery_factor = ed * es
    
    return recovery_factor


def water_drive_recovery_efficiency(
    porosity: float,
    water_saturation: float,
    initial_oil_fvf: float,
    permeability: float,
    water_viscosity: float,
    oil_viscosity: float,
    initial_pressure: float,
    final_pressure: float
) -> float:
    """
    Calculate water-drive recovery efficiency.
    
    Parameters:
    -----------
    porosity : float
        Porosity (fraction)
    water_saturation : float
        Water saturation (fraction)
    initial_oil_fvf : float
        Oil FVF at initial conditions (RB/STB)
    permeability : float
        Permeability (D)
    water_viscosity : float
        Water viscosity (cP)
    oil_viscosity : float
        Oil viscosity (cP)
    initial_pressure : float
        Initial pressure (psi)
    final_pressure : float
        Final pressure (psi)
        
    Returns:
    --------
    float
        Fractional recovery efficiency (fraction)
        
    Reference:
    ----------
    Craig Jr. F. F., 2004, The Reservoir Engineering Aspects of Waterflooding, 
    Vol. 3. Richardson, Texas: Monograph Series, SPE, Page: 83.
    """
    term1 = 54.898 * porosity * (1 - water_saturation) / initial_oil_fvf
    term2 = (permeability * water_viscosity / oil_viscosity)**0.0422
    term3 = (water_saturation)**(-0.0770)
    term4 = (water_saturation)**(-0.1903)
    term5 = (initial_pressure / final_pressure)**(-0.2159)
    
    return term1**0.0422 * term2 * term3 * term4 * term5


def water_formation_volume_factor_mccain(
    temperature: float,
    pressure: float
) -> float:
    """
    Calculate water formation volume factor using McCain correlation.
    
    Parameters:
    -----------
    temperature : float
        Temperature (°F)
    pressure : float
        Pressure (psi)
        
    Returns:
    --------
    float
        Water formation volume factor (bbl/STB)
        
    Reference:
    ----------
    Applied Petroleum Reservoir Engineering, Second Edition, 
    Craft & Hawkins, Page: 45.
    """
    Bw = (1.0001002 + 1.33391e-4 * temperature + 5.50654e-7 * temperature**2 -
          1.1953e-9 * pressure * temperature - 1.72834e-13 * pressure**2 * temperature -
          3.58922e-7 * pressure - 2.25341e-10 * pressure**2)
    
    return Bw


def material_balance_havlena_odeh(
    initial_oil_in_place: float,
    oil_fvf: float,
    initial_oil_fvf: float,
    solution_gor: float,
    initial_solution_gor: float,
    gas_fvf: float,
    cumulative_oil_production: float,
    cumulative_gas_production: float,
    cumulative_water_influx: float = 0.0
) -> float:
    """
    Calculate material balance for cumulative water influx using Havlena and Odeh method.
    
    Parameters:
    -----------
    initial_oil_in_place : float
        Initial oil in place (STB)
    oil_fvf : float
        Current oil formation volume factor (bbl/STB)
    initial_oil_fvf : float
        Initial oil formation volume factor (bbl/STB)
    solution_gor : float
        Current solution GOR (SCF/STB)
    initial_solution_gor : float
        Initial solution GOR (SCF/STB)
    gas_fvf : float
        Gas formation volume factor (bbl/SCF)
    cumulative_oil_production : float
        Cumulative oil production (STB)
    cumulative_gas_production : float
        Cumulative gas production (SCF)
    cumulative_water_influx : float, optional
        Cumulative water influx (bbl), default 0.0
        
    Returns:
    --------
    float
        Underground fluid withdrawal (bbl)
        
    Reference:
    ----------
    Havlena and Odeh material balance method.
    """
    # Oil expansion
    oil_expansion = initial_oil_in_place * (oil_fvf - initial_oil_fvf)
    
    # Solution gas expansion
    solution_gas_expansion = initial_oil_in_place * (initial_solution_gor - solution_gor) * gas_fvf
    
    # Production terms
    oil_production = cumulative_oil_production * oil_fvf
    gas_production = (cumulative_gas_production - cumulative_oil_production * solution_gor) * gas_fvf
    
    # Material balance: F = N * (Eo + Efw) + We
    underground_withdrawal = oil_expansion + solution_gas_expansion + cumulative_water_influx
    total_production = oil_production + gas_production
    
    return underground_withdrawal - total_production


def fraction_solution_gas_retained_reservoir(gas_oil_ratio_initial, gas_oil_ratio_current, oil_formation_volume_factor_initial, oil_formation_volume_factor_current):
    """
    Calculate fraction of total solution gas retained in reservoir as free gas.
    Formula 1.36 from additional_knowledge.tex
    
    Args:
        gas_oil_ratio_initial (float): Initial gas-oil ratio (scf/STB)
        gas_oil_ratio_current (float): Current gas-oil ratio (scf/STB)
        oil_formation_volume_factor_initial (float): Initial oil FVF (bbl/STB)
        oil_formation_volume_factor_current (float): Current oil FVF (bbl/STB)
    
    Returns:
        float: Fraction of solution gas retained as free gas
    """
    # Calculate gas release per barrel of oil
    gas_released = (gas_oil_ratio_initial * oil_formation_volume_factor_initial - 
                   gas_oil_ratio_current * oil_formation_volume_factor_current)
    
    # Fraction retained as free gas
    fraction_retained = gas_released / (gas_oil_ratio_initial * oil_formation_volume_factor_initial)
    
    return fraction_retained

def free_gas_in_place(original_oil_in_place, gas_oil_ratio_initial, oil_formation_volume_factor_initial, gas_formation_volume_factor):
    """
    Calculate free gas in place.
    Formula 1.38 from additional_knowledge.tex
    
    Args:
        original_oil_in_place (float): Original oil in place (STB)
        gas_oil_ratio_initial (float): Initial gas-oil ratio (scf/STB)
        oil_formation_volume_factor_initial (float): Initial oil FVF (bbl/STB)
        gas_formation_volume_factor (float): Gas formation volume factor (bbl/scf)
    
    Returns:
        float: Free gas in place (scf)
    """
    # Free gas initially dissolved in oil
    dissolved_gas = original_oil_in_place * gas_oil_ratio_initial
    
    # Convert to reservoir conditions
    free_gas = dissolved_gas * oil_formation_volume_factor_initial / gas_formation_volume_factor
    
    return free_gas

def gas_cap_ratio(gas_cap_volume, oil_zone_volume):
    """
    Calculate gas cap ratio.
    Formula 1.41 from additional_knowledge.tex
    
    Args:
        gas_cap_volume (float): Gas cap volume (bbl)
        oil_zone_volume (float): Oil zone volume (bbl)
    
    Returns:
        float: Gas cap ratio (dimensionless)
    """
    return gas_cap_volume / oil_zone_volume

def gas_cap_shrinkage(initial_gas_cap_volume, current_pressure, initial_pressure, gas_compressibility_factor_initial, gas_compressibility_factor_current):
    """
    Calculate gas cap shrinkage.
    Formula 1.42 from additional_knowledge.tex
    
    Args:
        initial_gas_cap_volume (float): Initial gas cap volume (bbl)
        current_pressure (float): Current pressure (psia)
        initial_pressure (float): Initial pressure (psia)
        gas_compressibility_factor_initial (float): Initial gas Z-factor
        gas_compressibility_factor_current (float): Current gas Z-factor
    
    Returns:
        float: Gas cap shrinkage volume (bbl)
    """
    # Calculate shrinkage based on pressure and compressibility changes
    shrinkage = initial_gas_cap_volume * (1.0 - (current_pressure * gas_compressibility_factor_initial) / 
                                         (initial_pressure * gas_compressibility_factor_current))
    
    return shrinkage

def initial_gas_cap(original_gas_in_place, gas_formation_volume_factor):
    """
    Calculate initial gas cap.
    Formula 1.71 from additional_knowledge.tex
    
    Args:
        original_gas_in_place (float): Original gas in place (scf)
        gas_formation_volume_factor (float): Gas formation volume factor (bbl/scf)
    
    Returns:
        float: Initial gas cap volume (bbl)
    """
    return original_gas_in_place * gas_formation_volume_factor

def hydrocarbon_pore_volume_evolved_gas(cumulative_oil_production, gas_oil_ratio_initial, gas_oil_ratio_current, oil_formation_volume_factor_current, gas_formation_volume_factor):
    """
    Calculate hydrocarbon pore volume occupied by evolved solution gas.
    Formula 1.65 from additional_knowledge.tex
    
    Args:
        cumulative_oil_production (float): Cumulative oil production (STB)
        gas_oil_ratio_initial (float): Initial gas-oil ratio (scf/STB)
        gas_oil_ratio_current (float): Current gas-oil ratio (scf/STB)
        oil_formation_volume_factor_current (float): Current oil FVF (bbl/STB)
        gas_formation_volume_factor (float): Gas formation volume factor (bbl/scf)
    
    Returns:
        float: Pore volume occupied by evolved gas (bbl)
    """
    # Gas evolved per barrel of oil produced
    gas_evolved = (gas_oil_ratio_initial - gas_oil_ratio_current) * cumulative_oil_production
    
    # Convert to reservoir volume
    pore_volume_gas = gas_evolved * gas_formation_volume_factor
    
    return pore_volume_gas

def hydrocarbon_pore_volume_gas_cap(gas_cap_volume_initial, current_pressure, initial_pressure, gas_compressibility_factor_initial, gas_compressibility_factor_current):
    """
    Calculate hydrocarbon pore volume occupied by gas cap.
    Formula 1.66 from additional_knowledge.tex
    
    Args:
        gas_cap_volume_initial (float): Initial gas cap volume (bbl)
        current_pressure (float): Current pressure (psia)
        initial_pressure (float): Initial pressure (psia)
        gas_compressibility_factor_initial (float): Initial gas Z-factor
        gas_compressibility_factor_current (float): Current gas Z-factor
    
    Returns:
        float: Current pore volume occupied by gas cap (bbl)
    """
    # Current gas cap volume accounting for pressure and compressibility changes
    current_volume = gas_cap_volume_initial * (current_pressure * gas_compressibility_factor_initial) / (initial_pressure * gas_compressibility_factor_current)
    
    return current_volume

def hydrocarbon_pore_volume_remaining_oil(original_oil_in_place, cumulative_oil_production, oil_formation_volume_factor_current):
    """
    Calculate hydrocarbon pore volume occupied by remaining oil.
    Formula 1.67 from additional_knowledge.tex
    
    Args:
        original_oil_in_place (float): Original oil in place (STB)
        cumulative_oil_production (float): Cumulative oil production (STB)
        oil_formation_volume_factor_current (float): Current oil FVF (bbl/STB)
    
    Returns:
        float: Pore volume occupied by remaining oil (bbl)
    """
    # Remaining oil in place
    remaining_oil = original_oil_in_place - cumulative_oil_production
    
    # Convert to reservoir volume
    pore_volume_oil = remaining_oil * oil_formation_volume_factor_current
    
    return pore_volume_oil

def incremental_cumulative_oil_production_undersaturated(original_oil_in_place, oil_compressibility, formation_compressibility, water_compressibility, water_saturation, pressure_drop):
    """
    Calculate incremental cumulative oil production in undersaturated reservoirs.
    Formula 1.69 from additional_knowledge.tex
    
    Args:
        original_oil_in_place (float): Original oil in place (STB)
        oil_compressibility (float): Oil compressibility (1/psi)
        formation_compressibility (float): Formation compressibility (1/psi)
        water_compressibility (float): Water compressibility (1/psi)
        water_saturation (float): Water saturation (fraction)
        pressure_drop (float): Pressure drop (psi)
    
    Returns:
        float: Incremental cumulative oil production (STB)
    """
    # Effective compressibility
    effective_compressibility = oil_compressibility + formation_compressibility + water_saturation * water_compressibility
    
    # Incremental production
    incremental_production = original_oil_in_place * effective_compressibility * pressure_drop
    
    return incremental_production

def water_influx_pot_aquifer_model(aquifer_volume, aquifer_compressibility, pressure_drop):
    """
    Calculate water influx using pot aquifer model.
    Formula 1.159 from additional_knowledge.tex
    
    Args:
        aquifer_volume (float): Aquifer volume (bbl)
        aquifer_compressibility (float): Aquifer compressibility (1/psi)
        pressure_drop (float): Pressure drop (psi)
    
    Returns:
        float: Water influx (bbl)
    """
    # Pot aquifer model for water influx
    water_influx = aquifer_volume * aquifer_compressibility * pressure_drop
    
    return water_influx


def line_source_solution_damaged_stimulated_wells(
    initial_pressure: float,
    time: float,
    permeability: float,
    volume_factor: float,
    porosity: float,
    compressibility: float,
    thickness: float,
    viscosity: float,
    wellbore_radius: float,
    flow_rate: float,
    skin_factor: float
) -> float:
    """
    Calculates line-source solution for damaged or stimulated wells.
    
    Args:
        initial_pressure (float): Initial pressure (psi)
        time (float): Time of production (h)
        permeability (float): Permeability (mD)
        volume_factor (float): Volume factor (RB/STB)
        porosity (float): Porosity (fraction)
        compressibility (float): Compressibility (1/psi)
        thickness (float): Thickness of reservoir (ft)
        viscosity (float): Viscosity of oil (cP)
        wellbore_radius (float): Radius of wellbore (ft)
        flow_rate (float): Flow rate (STB/day)
        skin_factor (float): Skin factor (dimensionless)
        
    Returns:
        float: Line-source solution for damaged or stimulated wells (psi)
        
    Reference:
        Pressure Transient Testing, Lee, Rollins & Spivey, Page: 11.
    """
    import math
    
    term1 = initial_pressure
    term2 = (70.6 * flow_rate * volume_factor * viscosity) / (permeability * thickness)
    term3 = math.log((1688 * porosity * viscosity * compressibility * wellbore_radius**2) / 
                     (permeability * time)) + 2 * skin_factor
    
    return term1 + term2 * term3


def low_pressure_gas_flow_rate_non_circular(
    permeability: float,
    thickness: float,
    reservoir_pressure: float,
    wellbore_flowing_pressure: float,
    avg_gas_viscosity: float,
    avg_gas_compressibility: float,
    drainage_area: float,
    shape_factor: float,
    wellbore_radius: float,
    skin: float,
    temperature: float
) -> float:
    """
    Calculates low-pressure region gas flow rate for non-circular drainage area.
    
    Args:
        permeability (float): Permeability (mD)
        thickness (float): Thickness (ft)
        reservoir_pressure (float): Average reservoir pressure (psi)
        wellbore_flowing_pressure (float): Well flowing pressure (psi)
        avg_gas_viscosity (float): Average gas viscosity (cP)
        avg_gas_compressibility (float): Average gas compressibility factor (dimensionless)
        drainage_area (float): Drainage area (ft²)
        shape_factor (float): Shape factor (dimensionless)
        wellbore_radius (float): Wellbore radius (ft)
        skin (float): Skin (dimensionless)
        temperature (float): Temperature (R)
        
    Returns:
        float: Gas flow rate (MSCF/day)
        
    Reference:
        Chapter 1, Formula 1.86
    """
    import math
    
    numerator = permeability * thickness * (reservoir_pressure**2 - wellbore_flowing_pressure**2)
    denominator = (1422 * avg_gas_viscosity * temperature * avg_gas_compressibility * 
                  (0.5 * math.log((4 * drainage_area) / (1.781 * shape_factor * wellbore_radius**2)) + skin))
    
    return numerator / denominator


def material_balance_cumulative_water_influx_havlena_odeh(
    initial_oil_in_place: float,
    oil_formation_volume_factor_initial: float,
    oil_formation_volume_factor: float,
    solution_gas_oil_ratio_initial: float,
    solution_gas_oil_ratio: float,
    gas_formation_volume_factor: float,
    cumulative_oil_production: float,
    cumulative_gas_production: float,
    initial_gas_cap: float,
    gas_expansion_factor: float
) -> float:
    """
    Calculates material balance for cumulative water influx using Havlena and Odeh method.
    
    Args:
        initial_oil_in_place (float): Initial oil in place (STB)
        oil_formation_volume_factor_initial (float): Initial oil formation volume factor (RB/STB)
        oil_formation_volume_factor (float): Current oil formation volume factor (RB/STB)
        solution_gas_oil_ratio_initial (float): Initial solution gas-oil ratio (SCF/STB)
        solution_gas_oil_ratio (float): Current solution gas-oil ratio (SCF/STB)
        gas_formation_volume_factor (float): Gas formation volume factor (RB/MSCF)
        cumulative_oil_production (float): Cumulative oil production (STB)
        cumulative_gas_production (float): Cumulative gas production (MSCF)
        initial_gas_cap (float): Initial gas cap (MSCF)
        gas_expansion_factor (float): Gas expansion factor (RB/MSCF)
        
    Returns:
        float: Cumulative water influx (RB)
        
    Reference:
        Chapter 1, Formula 1.87 - Material balance for cumulative water influx—Havlena and Odeh
    """
    # Underground withdrawal
    underground_withdrawal = (initial_oil_in_place * 
                             ((oil_formation_volume_factor - oil_formation_volume_factor_initial) +
                              (solution_gas_oil_ratio_initial - solution_gas_oil_ratio) * 
                              gas_formation_volume_factor / 1000))
    
    # Gas cap expansion
    gas_cap_expansion = initial_gas_cap * gas_expansion_factor
    
    # Production
    production = (cumulative_oil_production * oil_formation_volume_factor + 
                 cumulative_gas_production * gas_formation_volume_factor / 1000)
    
    # Water influx
    return underground_withdrawal + gas_cap_expansion - production


def oil_bubble_radius_circular_drainage(
    drainage_area: float
) -> float:
    """
    Calculates oil bubble radius of the drainage area of each well represented by a circle.
    
    Args:
        drainage_area (float): Drainage area (ft²)
        
    Returns:
        float: Oil bubble radius (ft)
        
    Reference:
        Chapter 1, Formula 1.92
    """
    import math
    return math.sqrt(drainage_area / math.pi)


def oil_in_place_undersaturated_no_injection(
    pore_volume: float,
    initial_oil_saturation: float,
    oil_formation_volume_factor_initial: float
) -> float:
    """
    Calculates oil in place for undersaturated oil reservoirs without fluid injection.
    
    Args:
        pore_volume (float): Pore volume (RB)
        initial_oil_saturation (float): Initial oil saturation (fraction)
        oil_formation_volume_factor_initial (float): Initial oil formation volume factor (RB/STB)
        
    Returns:
        float: Oil in place (STB)
        
    Reference:
        Chapter 1, Formula 1.97
    """
    return (pore_volume * initial_oil_saturation) / oil_formation_volume_factor_initial


def oil_in_place_saturated_reservoirs(
    pore_volume: float,
    initial_oil_saturation: float,
    oil_formation_volume_factor_bubble_point: float
) -> float:
    """
    Calculates oil in place in saturated oil reservoirs.
    
    Args:
        pore_volume (float): Pore volume (RB)
        initial_oil_saturation (float): Initial oil saturation (fraction)
        oil_formation_volume_factor_bubble_point (float): Oil formation volume factor at bubble point (RB/STB)
        
    Returns:
        float: Oil in place (STB)
        
    Reference:
        Chapter 1, Formula 1.98
    """
    return (pore_volume * initial_oil_saturation) / oil_formation_volume_factor_bubble_point


def oil_saturation_below_bubble_point(
    initial_oil_saturation: float,
    oil_formation_volume_factor: float,
    oil_formation_volume_factor_bubble_point: float,
    solution_gas_oil_ratio: float,
    solution_gas_oil_ratio_bubble_point: float,
    gas_formation_volume_factor: float
) -> float:
    """
    Calculates oil saturation at any depletion state below the bubble point pressure.
    
    Args:
        initial_oil_saturation (float): Initial oil saturation (fraction)
        oil_formation_volume_factor (float): Current oil formation volume factor (RB/STB)
        oil_formation_volume_factor_bubble_point (float): Oil formation volume factor at bubble point (RB/STB)
        solution_gas_oil_ratio (float): Current solution gas-oil ratio (SCF/STB)
        solution_gas_oil_ratio_bubble_point (float): Solution gas-oil ratio at bubble point (SCF/STB)
        gas_formation_volume_factor (float): Gas formation volume factor (RB/MSCF)
        
    Returns:
        float: Oil saturation (fraction)
        
    Reference:
        Chapter 1, Formula 1.100
    """
    numerator = (initial_oil_saturation * 
                (oil_formation_volume_factor - 
                 (solution_gas_oil_ratio_bubble_point - solution_gas_oil_ratio) * 
                 gas_formation_volume_factor / 1000))
    
    return numerator / oil_formation_volume_factor_bubble_point

def communication_factor_tight_gas(
    permeability: float,
    area: float,
    temperature: float,
    compartment_length: float
) -> float:
    """
    Calculates communication factor in a compartment in tight gas reservoirs.
    
    Args:
        permeability (float): Permeability (mD)
        area (float): Area (ft²)
        temperature (float): Temperature (°R)
        compartment_length (float): Length of compartment (ft)
        
    Returns:
        float: Communication factor (SCF/d/psi²/cP)
        
    Reference:
        Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
        Gulf Publishing of Elsevier, Chapter: 3, Page: 235.
    """
    return (0.111924 * permeability * area) / (temperature * compartment_length)


def compressibility_drive_index(
    gas_in_place: float,
    gas_expansion_factor: float,
    gas_fvf: float,
    gas_produced: float
) -> float:
    """
    Calculates compressibility drive index in gas reservoirs.
    
    Args:
        gas_in_place (float): Gas in place (MSCF)
        gas_expansion_factor (float): Gas compressibility drive (ft³/MSCF)
        gas_fvf (float): Gas formation volume factor (MSCF/ft³)
        gas_produced (float): Gas produced (MSCF)
        
    Returns:
        float: Compressibility index (dimensionless)
        
    Reference:
        Ahmed, T. & McKinney, P. D. Advanced Reservoir Engineering, 
        Gulf Publishing House, Burlington, MA, 2015.
    """
    return (gas_in_place * gas_expansion_factor) / (gas_fvf * gas_produced)


def crossflow_index(
    recovery_with_crossflow: float,
    recovery_no_crossflow: float,
    recovery_uniform_system: float
) -> float:
    """
    Calculates crossflow index for layered systems.
    
    Args:
        recovery_with_crossflow (float): Oil recovery from layered system with crossflow (STB)
        recovery_no_crossflow (float): Oil recovery from stratified system with no crossflow (STB)
        recovery_uniform_system (float): Oil recovery from uniform system with average permeability (STB)
        
    Returns:
        float: Crossflow index (dimensionless)
        
    Reference:
        Willhite, G.P. 1986. Waterflooding, Vol. 3. Richardson, Texas: 
        Textbook Series, SPE, Chapter: 2, Page: 166.
    """
    return (recovery_with_crossflow - recovery_no_crossflow) / (recovery_uniform_system - recovery_no_crossflow)


def cumulative_effective_compressibility_fetkovich(
    initial_water_saturation: float,
    water_compressibility: float,
    volume_ratio: float,
    formation_compressibility: float
) -> float:
    """
    Calculates cumulative effective compressibility using Fetkovich method.
    
    Args:
        initial_water_saturation (float): Initial water saturation (fraction)
        water_compressibility (float): Cumulative total water compressibility (1/psi)
        volume_ratio (float): Dimensionless volume ratio (dimensionless)
        formation_compressibility (float): Total PV (formation) compressibility (1/psi)
        
    Returns:
        float: Effective compressibility (1/psi)
        
    Reference:
        Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
        Gulf Publishing of Elsevier, Chapter: 3, Page: 215,216.
    """
    numerator = (initial_water_saturation * water_compressibility + 
                volume_ratio * (formation_compressibility + water_compressibility) + 
                formation_compressibility)
    denominator = 1 - initial_water_saturation
    
    return numerator / denominator


def cumulative_gas_production_tarner(
    initial_oil_in_place: float,
    initial_gas_solubility: float,
    current_gas_solubility: float,
    initial_oil_fvf: float,
    current_oil_fvf: float,
    gas_fvf: float,
    cumulative_oil_production: float
) -> float:
    """
    Calculates cumulative gas production using Tarner's method.
    
    Args:
        initial_oil_in_place (float): Initial oil-in-place (STB)
        initial_gas_solubility (float): Initial gas solubility (SCF/STB)
        current_gas_solubility (float): Gas solubility at current pressure (SCF/STB)
        initial_oil_fvf (float): Oil formation volume factor at initial pressure (bbl/STB)
        current_oil_fvf (float): Oil formation volume factor at current pressure (bbl/STB)
        gas_fvf (float): Gas formation volume factor at current pressure (bbl/SCF)
        cumulative_oil_production (float): Cumulative oil production (STB)
        
    Returns:
        float: Cumulative gas production (SCF)
        
    Reference:
        Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
        Gulf Publishing of Elsevier, Chapter: 5, Page: 340.
    """
    solution_gas_term = initial_oil_in_place * (initial_gas_solubility - current_gas_solubility)
    expansion_term = initial_oil_in_place * (initial_oil_fvf - current_oil_fvf) / gas_fvf
    produced_gas_term = cumulative_oil_production * (current_oil_fvf / gas_fvf - current_gas_solubility)
    
    return solution_gas_term - expansion_term - produced_gas_term


def deliverability_coefficient_shallow_gas(
    permeability: float,
    thickness: float,
    temperature: float,
    viscosity: float,
    z_factor: float,
    drainage_radius: float,
    wellbore_radius: float
) -> float:
    """
    Calculates performance coefficient for shallow gas reservoirs.
    
    Args:
        permeability (float): Permeability (mD)
        thickness (float): Thickness (ft)
        temperature (float): Temperature (°R)
        viscosity (float): Viscosity (cP)
        z_factor (float): Compressibility factor (dimensionless)
        drainage_radius (float): Radius of drainage area (ft)
        wellbore_radius (float): Wellbore radius (ft)
        
    Returns:
        float: Performance coefficient (dimensionless)
        
    Reference:
        Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
        Gulf Publishing of Elsevier, Chapter: 3, Page: 287.
    """
    return (permeability * thickness) / (1422 * temperature * viscosity * z_factor * 
                                        math.log(drainage_radius / wellbore_radius) - 0.5)


def dimensionless_pressure_kamal_brigham(
    flow_rate: float,
    permeability: float,
    thickness: float,
    viscosity: float,
    pressure_initial: float,
    pressure_current: float
) -> float:
    """
    Calculates dimensionless pressure using Kamal and Brigham method.
    
    Args:
        flow_rate (float): Flow rate (STB/day)
        permeability (float): Average permeability (mD)
        thickness (float): Thickness (ft)
        viscosity (float): Viscosity (cP)
        pressure_initial (float): Initial pressure (psi)
        pressure_current (float): Current pressure (psi)
        
    Returns:
        float: Dimensionless pressure (dimensionless)
        
    Reference:
        Kamal, M. M. and Brigham, W. E. 1975. Pulse-Testing Response for 
        Unequal Pulse and Shut-In Periods. SPE 5027.
    """
    return (2 * math.pi * permeability * thickness * (pressure_initial - pressure_current)) / (141.2 * flow_rate * viscosity)


def formation_temperature_gradient(
    surface_temperature: float,
    geothermal_gradient: float,
    depth: float
) -> float:
    """
    Calculates formation temperature for a given gradient.
    
    Args:
        surface_temperature (float): Surface temperature (°F)
        geothermal_gradient (float): Geothermal gradient (°F/ft)
        depth (float): Depth (ft)
        
    Returns:
        float: Formation temperature (°F)
        
    Reference:
        Standard petroleum engineering calculations
    """
    return surface_temperature + geothermal_gradient * depth


def gas_bubble_radius(
    surface_tension: float,
    pressure_difference: float
) -> float:
    """
    Calculates gas bubble radius using surface tension and pressure difference.
    
    Args:
        surface_tension (float): Surface tension (dyn/cm)
        pressure_difference (float): Pressure difference across bubble interface (dyn/cm²)
        
    Returns:
        float: Gas bubble radius (cm)
        
    Reference:
        Young-Laplace equation for spherical bubbles
    """
    return (2 * surface_tension) / pressure_difference


def gas_cap_ratio(
    initial_gas_cap_volume: float,
    initial_oil_volume: float
) -> float:
    """
    Calculates gas cap ratio.
    
    Args:
        initial_gas_cap_volume (float): Initial gas cap volume (bbl)
        initial_oil_volume (float): Initial oil volume (bbl)
        
    Returns:
        float: Gas cap ratio (dimensionless)
        
    Reference:
        Standard reservoir engineering calculations
    """
    return initial_gas_cap_volume / initial_oil_volume


def gas_expansion_factor(
    initial_z_factor: float,
    current_z_factor: float,
    initial_pressure: float,
    current_pressure: float
) -> float:
    """
    Calculates gas expansion factor.
    
    Args:
        initial_z_factor (float): Initial z-factor (dimensionless)
        current_z_factor (float): Current z-factor (dimensionless)
        initial_pressure (float): Initial pressure (psi)
        current_pressure (float): Current pressure (psi)
        
    Returns:
        float: Gas expansion factor (dimensionless)
        
    Reference:
        Standard gas reservoir engineering
    """
    return (initial_z_factor * current_pressure) / (current_z_factor * initial_pressure) - 1


def hydrostatic_pressure_gradient(
    fluid_density: float,
    gravity: float = 32.174
) -> float:
    """
    Calculates hydrostatic pressure gradient.
    
    Args:
        fluid_density (float): Fluid density (lb/ft³)
        gravity (float, optional): Gravitational acceleration (ft/s²). Defaults to 32.174.
        
    Returns:
        float: Hydrostatic pressure gradient (psi/ft)
        
    Reference:
        Standard fluid mechanics
    """
    return fluid_density * gravity / 144  # Convert from lb/ft² to psi


def leverett_j_function(
    capillary_pressure: float,
    porosity: float,
    permeability: float,
    interfacial_tension: float,
    contact_angle: float
) -> float:
    """
    Calculates Leverett J-function for capillary pressure correlation.
    
    Args:
        capillary_pressure (float): Capillary pressure (psi)
        porosity (float): Porosity (fraction)
        permeability (float): Permeability (mD)
        interfacial_tension (float): Interfacial tension (dyn/cm)
        contact_angle (float): Contact angle (degrees)
        
    Returns:
        float: Leverett J-function (dimensionless)
        
    Reference:
        Leverett, M.C. 1941. Capillary Behavior in Porous Solids. 
        Trans. AIME 142: 152-169.
    """
    contact_angle_rad = math.radians(contact_angle)
    return (capillary_pressure * math.sqrt(permeability / porosity)) / (interfacial_tension * math.cos(contact_angle_rad))
