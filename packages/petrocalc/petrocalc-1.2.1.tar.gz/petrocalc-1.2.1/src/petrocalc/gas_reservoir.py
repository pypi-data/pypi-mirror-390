"""
Gas reservoir engineering calculations.

This module contains functions specifically for gas reservoir engineering including:
- Gas material balance
- Gas well deliverability
- Gas expansion and drive mechanisms
- Coalbed methane calculations
- Gas reservoir performance
- Unconventional gas calculations
"""

import math
from typing import Union, Tuple, Optional


def gas_material_balance(
    initial_gas_in_place: float,
    gas_expansion_factor: float,
    cumulative_water_influx: float = 0
) -> float:
    """
    Calculates gas material balance equation.
    
    Args:
        initial_gas_in_place (float): Initial gas in place (MSCF)
        gas_expansion_factor (float): Gas expansion factor (bbl/MSCF)
        cumulative_water_influx (float): Cumulative water influx (bbl), default 0
        
    Returns:
        float: Underground fluid withdrawal (bbl)
        
    Reference:
        Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering
    """
    g = initial_gas_in_place
    eg = gas_expansion_factor
    we = cumulative_water_influx
    
    # Material balance equation
    f = g * eg + we
    
    return f


def gas_expansion_factor(
    initial_z_factor: float,
    current_z_factor: float,
    initial_pressure: float,
    current_pressure: float,
    initial_temperature: float,
    current_temperature: float
) -> float:
    """
    Calculates gas expansion factor.
    
    Args:
        initial_z_factor (float): Initial gas compressibility factor (dimensionless)
        current_z_factor (float): Current gas compressibility factor (dimensionless)
        initial_pressure (float): Initial pressure (psia)
        current_pressure (float): Current pressure (psia)
        initial_temperature (float): Initial temperature (°R)
        current_temperature (float): Current temperature (°R)
        
    Returns:
        float: Gas expansion factor (bbl/MSCF)
        
    Reference:
        Standard gas reservoir engineering
    """
    zi = initial_z_factor
    z = current_z_factor
    pi = initial_pressure
    p = current_pressure
    ti = initial_temperature
    t = current_temperature
    
    # Gas expansion factor
    eg = (zi * p * ti) / (z * pi * t)
    
    return eg


def gas_formation_volume_factor_detailed(
    pressure: float,
    temperature: float,
    z_factor: float
) -> float:
    """
    Calculates gas formation volume factor with detailed calculation.
    
    Args:
        pressure (float): Pressure (psia)
        temperature (float): Temperature (°R)
        z_factor (float): Gas compressibility factor (dimensionless)
        
    Returns:
        float: Gas formation volume factor (bbl/scf)
        
    Reference:
        Standard gas reservoir engineering
    """
    p = pressure
    t = temperature
    z = z_factor
    
    # Standard conditions: 14.7 psia, 520°R
    p_sc = 14.7
    t_sc = 520
    
    # Gas FVF
    bg = (z * t * p_sc) / (p * t_sc)
    
    return bg


def gas_drive_index(
    gas_cap_size: float,
    oil_zone_size: float,
    gas_expansion_factor: float
) -> float:
    """
    Calculates gas drive index for gas reservoirs.
    
    Args:
        gas_cap_size (float): Gas cap size (MSCF)
        oil_zone_size (float): Oil zone size (STB)
        gas_expansion_factor (float): Gas expansion factor (dimensionless)
        
    Returns:
        float: Gas drive index (dimensionless)
        
    Reference:
        Reservoir engineering drive mechanism calculations
    """
    g = gas_cap_size
    n = oil_zone_size
    eg = gas_expansion_factor
    
    if n <= 0:
        return 0
    
    # Gas drive index
    gdi = (g * eg) / n
    
    return gdi


def water_drive_index_gas(
    cumulative_water_influx: float,
    initial_gas_in_place: float,
    gas_expansion_factor: float
) -> float:
    """
    Calculates water-drive index for gas reservoirs.
    
    Args:
        cumulative_water_influx (float): Cumulative water influx (bbl)
        initial_gas_in_place (float): Initial gas in place (MSCF)
        gas_expansion_factor (float): Gas expansion factor (bbl/MSCF)
        
    Returns:
        float: Water-drive index (dimensionless)
        
    Reference:
        Gas reservoir drive mechanism analysis
    """
    we = cumulative_water_influx
    g = initial_gas_in_place
    eg = gas_expansion_factor
    
    denominator = g * eg
    
    if denominator <= 0:
        return 0
    
    # Water drive index
    wdi = we / denominator
    
    return wdi


def water_expansion_term_gas(
    connate_water_saturation: float,
    water_compressibility: float,
    pressure_drop: float
) -> float:
    """
    Calculates water expansion term in gas reservoirs.
    
    Args:
        connate_water_saturation (float): Connate water saturation (fraction)
        water_compressibility (float): Water compressibility (1/psi)
        pressure_drop (float): Pressure drop (psi)
        
    Returns:
        float: Water expansion term (dimensionless)
        
    Reference:
        Gas reservoir material balance calculations
    """
    swi = connate_water_saturation
    cw = water_compressibility
    dp = pressure_drop
    
    # Water expansion term
    we_term = swi * cw * dp
    
    return we_term


def initial_gas_in_place_water_drive(
    reservoir_area: float,
    net_pay: float,
    porosity: float,
    initial_water_saturation: float,
    initial_gas_formation_volume_factor: float
) -> float:
    """
    Calculates initial gas in place for water-drive gas reservoirs.
    
    Args:
        reservoir_area (float): Reservoir area (acres)
        net_pay (float): Net pay thickness (ft)
        porosity (float): Porosity (fraction)
        initial_water_saturation (float): Initial water saturation (fraction)
        initial_gas_formation_volume_factor (float): Initial gas FVF (bbl/scf)
        
    Returns:
        float: Initial gas in place (MSCF)
        
    Reference:
        Volumetric calculations for gas reservoirs
    """
    a = reservoir_area
    h = net_pay
    phi = porosity
    swi = initial_water_saturation
    bgi = initial_gas_formation_volume_factor
    
    # Convert acres to ft²
    area_ft2 = a * 43560
    
    # Bulk volume
    bulk_volume = area_ft2 * h
    
    # Pore volume
    pore_volume = bulk_volume * phi
    
    # Hydrocarbon pore volume
    hc_pore_volume = pore_volume * (1 - swi)
    
    # Convert to barrels
    hc_pv_bbl = hc_pore_volume / 5.615
    
    # Initial gas in place
    g = hc_pv_bbl / bgi / 1000  # Convert to MSCF
    
    return g


def gas_saturation_water_drive(
    initial_gas_saturation: float,
    cumulative_gas_production: float,
    initial_gas_in_place: float,
    cumulative_water_influx: float,
    pore_volume: float
) -> float:
    """
    Calculates gas saturation in water-drive gas reservoirs.
    
    Args:
        initial_gas_saturation (float): Initial gas saturation (fraction)
        cumulative_gas_production (float): Cumulative gas production (MSCF)
        initial_gas_in_place (float): Initial gas in place (MSCF)
        cumulative_water_influx (float): Cumulative water influx (bbl)
        pore_volume (float): Pore volume (bbl)
        
    Returns:
        float: Current gas saturation (fraction)
        
    Reference:
        Gas reservoir material balance
    """
    sgi = initial_gas_saturation
    gp = cumulative_gas_production
    g = initial_gas_in_place
    we = cumulative_water_influx
    pv = pore_volume
    
    # Current gas saturation
    sg = sgi * (1 - gp / g) - we / pv
    
    return max(0, min(1, sg))


def gas_adsorbed_coalbed_methane(
    langmuir_pressure: float,
    langmuir_volume: float,
    reservoir_pressure: float
) -> float:
    """
    Calculates gas adsorbed in coalbed methane reservoirs.
    
    Args:
        langmuir_pressure (float): Langmuir pressure (psia)
        langmuir_volume (float): Langmuir volume (scf/ton)
        reservoir_pressure (float): Reservoir pressure (psia)
        
    Returns:
        float: Gas adsorbed (scf/ton)
        
    Reference:
        Langmuir isotherm for coalbed methane
    """
    pl = langmuir_pressure
    vl = langmuir_volume
    p = reservoir_pressure
    
    # Langmuir isotherm
    va = (vl * p) / (pl + p)
    
    return va


def gas_solubility_coalbed_methane(
    reservoir_pressure: float,
    reservoir_temperature: float,
    henry_constant: float = 1.0
) -> float:
    """
    Calculates gas solubility in coalbed methane reservoirs.
    
    Args:
        reservoir_pressure (float): Reservoir pressure (psia)
        reservoir_temperature (float): Reservoir temperature (°R)
        henry_constant (float): Henry's law constant (scf/bbl/psi), default 1.0
        
    Returns:
        float: Gas solubility (scf/bbl)
        
    Reference:
        Henry's law for gas solubility in water
    """
    p = reservoir_pressure
    t = reservoir_temperature
    h = henry_constant
    
    # Henry's law (simplified)
    solubility = h * p / t
    
    return max(0, solubility)


def remaining_gas_coalbed_methane(
    original_gas_content: float,
    cumulative_production: float,
    desorption_efficiency: float = 0.8
) -> float:
    """
    Calculates remaining gas in place in coalbed methane reservoirs.
    
    Args:
        original_gas_content (float): Original gas content (scf/ton)
        cumulative_production (float): Cumulative gas production (scf/ton)
        desorption_efficiency (float): Desorption efficiency (fraction), default 0.8
        
    Returns:
        float: Remaining gas in place (scf/ton)
        
    Reference:
        Coalbed methane reservoir calculations
    """
    gc = original_gas_content
    gp = cumulative_production
    eff = desorption_efficiency
    
    # Remaining gas accounting for desorption efficiency
    remaining = gc - (gp / eff)
    
    return max(0, remaining)


def volume_gas_adsorbed_coalbed(
    coal_density: float,
    reservoir_area: float,
    coal_thickness: float,
    gas_content: float
) -> float:
    """
    Calculates volume of gas adsorbed in coalbed methane reservoirs.
    
    Args:
        coal_density (float): Coal density (tons/acre-ft)
        reservoir_area (float): Reservoir area (acres)
        coal_thickness (float): Coal thickness (ft)
        gas_content (float): Gas content (scf/ton)
        
    Returns:
        float: Volume of adsorbed gas (MSCF)
        
    Reference:
        Coalbed methane volumetric calculations
    """
    rho_coal = coal_density
    area = reservoir_area
    h = coal_thickness
    gc = gas_content
    
    # Total coal mass
    coal_mass = rho_coal * area * h
    
    # Total adsorbed gas
    va = coal_mass * gc / 1000  # Convert to MSCF
    
    return va


def fractional_gas_recovery_coalbed(
    reservoir_pressure: float,
    critical_desorption_pressure: float,
    langmuir_pressure: float
) -> float:
    """
    Calculates fractional gas recovery below critical desorption pressure in coalbed methane.
    
    Args:
        reservoir_pressure (float): Current reservoir pressure (psia)
        critical_desorption_pressure (float): Critical desorption pressure (psia)
        langmuir_pressure (float): Langmuir pressure (psia)
        
    Returns:
        float: Fractional gas recovery (fraction)
        
    Reference:
        Coalbed methane desorption calculations
    """
    p = reservoir_pressure
    pcd = critical_desorption_pressure
    pl = langmuir_pressure
    
    if p >= pcd:
        return 0  # No desorption above critical pressure
    
    # Fractional recovery based on pressure decline
    if pl + p > 0:
        fr = (pcd - p) / (pl + p)
    else:
        fr = 0
    
    return max(0, min(1, fr))


def compressibility_drive_gas(
    gas_compressibility: float,
    pressure_drop: float
) -> float:
    """
    Calculates compressibility drive in gas reservoirs.
    
    Args:
        gas_compressibility (float): Gas compressibility (1/psi)
        pressure_drop (float): Pressure drop (psi)
        
    Returns:
        float: Compressibility drive factor (dimensionless)
        
    Reference:
        Gas reservoir drive mechanisms
    """
    cg = gas_compressibility
    dp = pressure_drop
    
    # Compressibility drive
    cd = cg * dp
    
    return cd


def gas_produced_by_expansion(
    initial_gas_in_place: float,
    initial_z_factor: float,
    current_z_factor: float,
    initial_pressure: float,
    current_pressure: float
) -> float:
    """
    Calculates gas produced by gas expansion.
    
    Args:
        initial_gas_in_place (float): Initial gas in place (MSCF)
        initial_z_factor (float): Initial z-factor (dimensionless)
        current_z_factor (float): Current z-factor (dimensionless)
        initial_pressure (float): Initial pressure (psia)
        current_pressure (float): Current pressure (psia)
        
    Returns:
        float: Gas produced by expansion (MSCF)
        
    Reference:
        Gas reservoir material balance
    """
    g = initial_gas_in_place
    zi = initial_z_factor
    z = current_z_factor
    pi = initial_pressure
    p = current_pressure
    
    # Gas produced by expansion
    gp_exp = g * (1 - (zi * p) / (z * pi))
    
    return max(0, gp_exp)


def cole_plot_underground_withdrawal(
    gas_in_place: float, 
    gas_expansion_term: float, 
    water_influx: float
) -> float:
    """
    Calculate underground fluid withdrawal using Cole plot method.
    
    Parameters:
    -----------
    gas_in_place : float
        Gas in place (MSCF)
    gas_expansion_term : float
        Gas expansion term (bbl/MSCF)
    water_influx : float
        Cumulative water influx (bbl)
        
    Returns:
    --------
    float
        Underground fluid withdrawal (bbl)
        
    Reference:
    ----------
    Ahmed, T., McKinney, P.D. Advanced Reservoir Engineering, 
    Gulf Publishing House, Burlington, MA, 2015.
    """
    return gas_in_place * gas_expansion_term + water_influx


def communication_factor_tight_gas(
    permeability: float, 
    area: float, 
    temperature: float, 
    length: float
) -> float:
    """
    Calculate communication factor for compartments in tight gas reservoirs.
    
    Parameters:
    -----------
    permeability : float
        Permeability (mD)
    area : float
        Area (ft²)
    temperature : float
        Temperature (°R)
    length : float
        Length of compartment (ft)
        
    Returns:
    --------
    float
        Communication factor (SCF/d/psi²/cP)
        
    Reference:
    ----------
    Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
    Gulf Publishing of Elsevier, Chapter: 3, Page: 235.
    """
    return 0.111924 * permeability * area / (temperature * length)


def hammerlindl_correction_factor(
    gas_in_place: float, 
    gas_produced: float, 
    gas_fvf: float, 
    rock_water_expansion: float
) -> float:
    """
    Calculate compressibility drive index using Hammerlindl correction factor.
    
    Parameters:
    -----------
    gas_in_place : float
        Gas in place (MSCF)
    gas_produced : float
        Gas produced (MSCF)
    gas_fvf : float
        Gas formation volume factor (bbl/MSCF)
    rock_water_expansion : float
        Rock and water expansion term (bbl/MSCF)
        
    Returns:
    --------
    float
        Compressibility drive index (dimensionless)
        
    Reference:
    ----------
    Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
    Gulf Publishing of Elsevier, Chapter: 3, Page: 211.
    """
    return (gas_in_place * rock_water_expansion) / (gas_produced * gas_fvf)


def crossflow_index(
    recovery_with_crossflow: float, 
    recovery_no_crossflow: float, 
    recovery_uniform: float
) -> float:
    """
    Calculate crossflow index for layered reservoir systems.
    
    Parameters:
    -----------
    recovery_with_crossflow : float
        Oil recovery from layered system with crossflow (STB)
    recovery_no_crossflow : float
        Oil recovery from stratified system with no crossflow (STB)
    recovery_uniform : float
        Oil recovery from uniform system with average permeability (STB)
        
    Returns:
    --------
    float
        Crossflow index (dimensionless)
        
    Reference:
    ----------
    Willhite, G.P. 1986. Waterflooding, Vol. 3. Richardson, Texas: 
    Textbook Series, SPE, Chapter: 2, Page: 166.
    """
    return (recovery_with_crossflow - recovery_no_crossflow) / (recovery_uniform - recovery_no_crossflow)


def cumulative_gas_production_tarner(
    initial_oil_in_place: float,
    initial_gas_solubility: float,
    current_gas_solubility: float,
    initial_oil_fvf: float,
    current_oil_fvf: float,
    current_gas_fvf: float,
    cumulative_oil_production: float
) -> float:
    """
    Calculate cumulative gas production using Tarner's method.
    
    Parameters:
    -----------
    initial_oil_in_place : float
        Initial oil in place (STB)
    initial_gas_solubility : float
        Initial gas solubility (SCF/STB)
    current_gas_solubility : float
        Gas solubility at current pressure (SCF/STB)
    initial_oil_fvf : float
        Oil formation volume factor at initial pressure (bbl/STB)
    current_oil_fvf : float
        Oil formation volume factor at current pressure (bbl/STB)
    current_gas_fvf : float
        Gas formation volume factor at current pressure (bbl/SCF)
    cumulative_oil_production : float
        Cumulative oil production (STB)
        
    Returns:
    --------
    float
        Cumulative gas production (SCF)
        
    Reference:
    ----------
    Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
    Gulf Publishing of Elsevier, Chapter: 5, Page: 340.
    """
    # First term: solution gas liberated from oil
    solution_gas = initial_oil_in_place * (initial_gas_solubility - current_gas_solubility) * \
                   (initial_oil_fvf - current_oil_fvf) / current_gas_fvf
    
    # Second term: solution gas produced with oil
    produced_gas = cumulative_oil_production * (current_oil_fvf / current_gas_fvf - current_gas_solubility)
    
    return solution_gas + produced_gas


def gas_expansion_term_gas_reservoirs(original_gas_in_place, gas_formation_volume_factor_initial, gas_formation_volume_factor_current):
    """
    Calculate gas expansion term in gas reservoirs.
    Formula 1.45 from additional_knowledge.tex
    
    Args:
        original_gas_in_place (float): Original gas in place (scf)
        gas_formation_volume_factor_initial (float): Initial gas FVF (bbl/scf)
        gas_formation_volume_factor_current (float): Current gas FVF (bbl/scf)
    
    Returns:
        float: Gas expansion term (bbl)
    """
    # Gas expansion due to pressure decline
    expansion_term = original_gas_in_place * (gas_formation_volume_factor_current - gas_formation_volume_factor_initial)
    
    return expansion_term

def pore_volume_injection_gas_water(injected_gas_volume, gas_formation_volume_factor, injected_water_volume, water_formation_volume_factor):
    """
    Calculate pore volume occupied by injection of gas and water.
    Formula 1.106 from additional_knowledge.tex
    
    Args:
        injected_gas_volume (float): Injected gas volume (scf)
        gas_formation_volume_factor (float): Gas formation volume factor (bbl/scf)
        injected_water_volume (float): Injected water volume (bbl)
        water_formation_volume_factor (float): Water formation volume factor (bbl/STB)
    
    Returns:
        float: Total pore volume occupied by injected fluids (bbl)
    """
    # Pore volume occupied by injected gas
    pv_gas = injected_gas_volume * gas_formation_volume_factor
    
    # Pore volume occupied by injected water
    pv_water = injected_water_volume * water_formation_volume_factor
    
    # Total pore volume
    total_pv = pv_gas + pv_water
    
    return total_pv

def pore_volume_squared_method_tight_gas(original_gas_in_place, porosity, reservoir_area, thickness, gas_compressibility_factor_initial, gas_compressibility_factor_current, pressure_initial, pressure_current):
    """
    Calculate pore volume through squared method in tight gas reservoirs.
    Formula 1.107 from additional_knowledge.tex
    
    Args:
        original_gas_in_place (float): Original gas in place (scf)
        porosity (float): Porosity (fraction)
        reservoir_area (float): Reservoir area (acres)
        thickness (float): Net pay thickness (ft)
        gas_compressibility_factor_initial (float): Initial gas Z-factor
        gas_compressibility_factor_current (float): Current gas Z-factor
        pressure_initial (float): Initial pressure (psia)
        pressure_current (float): Current pressure (psia)
    
    Returns:
        float: Pore volume calculated using squared method (bbl)
    """
    import math
    
    # Convert area to ft²
    area_ft2 = reservoir_area * 43560
    
    # Bulk volume
    bulk_volume = area_ft2 * thickness / 5.615  # Convert to bbl
    
    # Pore volume
    pore_volume = bulk_volume * porosity
    
    # Pressure-compressibility correction using squared method
    pressure_ratio_squared = (pressure_current * gas_compressibility_factor_initial)**2 / (pressure_initial * gas_compressibility_factor_current)**2
    
    # Corrected pore volume
    corrected_pv = pore_volume * math.sqrt(pressure_ratio_squared)
    
    return corrected_pv

def roach_plot_abnormally_pressured_gas(cumulative_production, pressure_data, compressibility_factor_data):
    """
    Calculate Roach plot parameters for abnormally pressured gas reservoirs.
    Formula 1.117 from additional_knowledge.tex
    
    Args:
        cumulative_production (list): Cumulative gas production data (scf)
        pressure_data (list): Pressure data (psia)
        compressibility_factor_data (list): Gas compressibility factor data
    
    Returns:
        dict: Dictionary containing Roach plot parameters
    """
    import math
    
    if len(cumulative_production) != len(pressure_data) or len(pressure_data) != len(compressibility_factor_data):
        return {'error': 'Data arrays must have same length'}
    
    # Calculate P/Z values
    p_over_z = [p / z for p, z in zip(pressure_data, compressibility_factor_data)]
    
    # Initial P/Z
    initial_p_over_z = p_over_z[0]
    
    # Roach plot parameters
    roach_parameters = []
    for i, gp in enumerate(cumulative_production):
        if i > 0:  # Skip initial point
            parameter = (initial_p_over_z - p_over_z[i]) / gp
            roach_parameters.append(parameter)
    
    return {
        'p_over_z_values': p_over_z,
        'initial_p_over_z': initial_p_over_z,
        'roach_parameters': roach_parameters
    }

def rock_expansion_term_abnormally_pressured_gas(original_gas_in_place, formation_compressibility, pressure_initial, pressure_current):
    """
    Calculate rock expansion term in abnormally pressured gas reservoirs.
    Formula 1.118 from additional_knowledge.tex
    
    Args:
        original_gas_in_place (float): Original gas in place (scf)
        formation_compressibility (float): Formation compressibility (1/psi)
        pressure_initial (float): Initial pressure (psia)
        pressure_current (float): Current pressure (psia)
    
    Returns:
        float: Rock expansion term (scf)
    """
    # Rock expansion due to pressure decline
    pressure_drop = pressure_initial - pressure_current
    expansion_term = original_gas_in_place * formation_compressibility * pressure_drop
    
    return expansion_term

def water_influx_constant_van_everdingen_hurst(aquifer_productivity_index, pressure_drop, dimensionless_time):
    """
    Calculate water influx constant for van Everdingen and Hurst unsteady-state model.
    Formula 1.160 from additional_knowledge.tex
    
    Args:
        aquifer_productivity_index (float): Aquifer productivity index (bbl/day/psi)
        pressure_drop (float): Pressure drop (psi)
        dimensionless_time (float): Dimensionless time
    
    Returns:
        float: Water influx (bbl)
    """
    import math
    
    # van Everdingen and Hurst water influx equation
    # Simplified form using dimensionless time
    if dimensionless_time > 0:
        time_function = math.log(dimensionless_time) + 0.5  # Simplified time function
        water_influx = aquifer_productivity_index * pressure_drop * time_function
    else:
        water_influx = 0.0
    
    return water_influx

def material_balance_cumulative_water_influx_havlena_odeh(original_oil_in_place, cumulative_oil_production, oil_formation_volume_factor_initial, oil_formation_volume_factor_current, cumulative_gas_production, gas_formation_volume_factor, initial_gas_cap_ratio):
    """
    Calculate material balance for cumulative water influx using Havlena and Odeh method.
    Formula 1.87 from additional_knowledge.tex
    
    Args:
        original_oil_in_place (float): Original oil in place (STB)
        cumulative_oil_production (float): Cumulative oil production (STB)
        oil_formation_volume_factor_initial (float): Initial oil FVF (bbl/STB)
        oil_formation_volume_factor_current (float): Current oil FVF (bbl/STB)
        cumulative_gas_production (float): Cumulative gas production (scf)
        gas_formation_volume_factor (float): Gas formation volume factor (bbl/scf)
        initial_gas_cap_ratio (float): Initial gas cap ratio
    
    Returns:
        float: Cumulative water influx (bbl)
    """
    # Underground withdrawal
    underground_withdrawal = cumulative_oil_production * oil_formation_volume_factor_current + cumulative_gas_production * gas_formation_volume_factor
    
    # Expansion of oil and dissolved gas
    oil_expansion = original_oil_in_place * (oil_formation_volume_factor_current - oil_formation_volume_factor_initial)
    
    # Gas cap expansion (if present)
    gas_cap_expansion = 0.0
    if initial_gas_cap_ratio > 0:
        gas_cap_expansion = original_oil_in_place * initial_gas_cap_ratio * oil_formation_volume_factor_initial * (1.0 / oil_formation_volume_factor_current - 1.0 / oil_formation_volume_factor_initial)
    
    # Water influx from material balance
    water_influx = underground_withdrawal - oil_expansion - gas_cap_expansion
    
    return water_influx
