"""
Facilities and Process Engineering Module

This module provides calculations for oil and gas facilities design and process
engineering including separators, columns, adsorption units, heat exchangers,
and process control systems.

Author: PetroCalc Development Team
Source: Chapter 12 - Facilities and process engineering formulas and calculations
"""

import math
from typing import Tuple, Optional, Union


def allowable_gas_velocity_separator(
    ks: float,
    liquid_density: float,
    gas_density: float
) -> float:
    """
    Calculate allowable gas velocity through gas separator.
    
    Args:
        ks: Empirical Gas Constant (ft/s)
        liquid_density: Liquid Density (g/cc)
        gas_density: Gas Density (g/cc)
    
    Returns:
        float: Allowable Gas Velocity (ft/s)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 73.
    """
    v = ks * ((liquid_density - gas_density) / gas_density)**0.5
    return v


def allowable_velocity_downcomer(
    height: float,
    residence_time: float
) -> float:
    """
    Calculate allowable velocity in downcomer for tray type tower.
    
    Args:
        height: Height of Liquid Downcomer (in.)
        residence_time: Residence Time (s)
    
    Returns:
        float: Allowable Velocity in Downcomer (in./s)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 73.
    """
    vd = height / residence_time
    return vd


def bed_diameter_adsorption_unit(
    flow_rate: float,
    relative_density: float,
    pressure_drop: float,
    area: float
) -> float:
    """
    Calculate capacity coefficient for adsorption unit bed diameter.
    
    Args:
        flow_rate: Flow Rate (bbl/m)
        relative_density: Fluid Relative Density (dimensionless)
        pressure_drop: Pressure Drop (psi)
        area: Cross-sectional area (ft²)
    
    Returns:
        float: Capacity Coefficient (dimensionless)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 1, Page: 265.
    """
    cv = (flow_rate / area) * (relative_density / pressure_drop)**0.5
    return cv


def bed_length_adsorption_unit(
    max_capacity: float,
    saturation_capacity: float,
    mtz_length: float
) -> float:
    """
    Calculate bed length of adsorption unit.
    
    Args:
        max_capacity: Maximum Desiccant Useful Capacity (kg water/100 kg desiccant)
        saturation_capacity: Dynamic Capacity at Saturation (kg water/100 kg desiccant)
        mtz_length: Mass Transfer Zone (MTZ) Length (ft)
    
    Returns:
        float: Bed Length (ft)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 388.
    """
    hb = (0.45 * mtz_length * saturation_capacity) / (saturation_capacity - max_capacity)
    return hb


def block_efficiency_factor(
    friction_factor: float,
    num_sheaves: int
) -> float:
    """
    Calculate block efficiency factor for drilling operations.
    
    Args:
        friction_factor: Friction Factor (unitless)
        num_sheaves: Number of Rolling Sheaves (unitless)
    
    Returns:
        float: Block Efficiency Factor (unitless)
    
    Reference:
        Samuel E. Robello. 501 Solved Problems and Calculations for Drilling Operations. 
        Sigma Quadrant. 2015. Houston, Texas, Page: 11.
    """
    numerator = friction_factor**num_sheaves - 1
    denominator = friction_factor**num_sheaves - num_sheaves * (friction_factor - 1)
    e = numerator / denominator
    return e


def bottom_distillation_column_rate(
    liquid_velocity: float,
    gas_velocity: float,
    gas_density: float,
    liquid_density: float
) -> float:
    """
    Calculate bottom distillation column rate.
    
    Args:
        liquid_velocity: Liquid Mass Velocity (lbm/ft²·h)
        gas_velocity: Gas Mass Velocity (lbm/ft²·h)
        gas_density: Gas Density (g/cc)
        liquid_density: Liquid Density (g/cc)
    
    Returns:
        float: Bottom Distillation Column Rate (dimensionless)
    
    Reference:
        Campbell, J. M., (1992, Houston, TX (United States)), Gas Conditioning and Processing, 
        Vol. 2, Campbell Petroleum Series, Page: 74.
    """
    x = (liquid_velocity * gas_density) / (gas_velocity * liquid_density)
    return x


def breakthrough_time_adsorption(
    capacity: float,
    bulk_density: float,
    bed_length: float,
    water_loading: float
) -> float:
    """
    Calculate breakthrough time in an adsorption unit.
    
    Args:
        capacity: Height of Unit (ft)
        bulk_density: Bulk Density of Desiccant (lb/ft³)
        bed_length: Bed Length of Unit (ft)
        water_loading: Water Loading (lb/ft²·h)
    
    Returns:
        float: Breakthrough Time (h)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 391.
    """
    y = (0.01 * capacity * bulk_density * bed_length) / water_loading
    return y


def breathing_loss_natural_gas(
    pressure: float,
    tank_diameter: float,
    paint_factor: float = 1.0,
    outage_factor: float = 1.0
) -> float:
    """
    Calculate breathing loss of natural gas from storage tank.
    
    Args:
        pressure: Pressure (psi)
        tank_diameter: Tank Diameter (ft)
        paint_factor: Paint Factor (dimensionless), default = 1.0
        outage_factor: Outage Factor (dimensionless), default = 1.0
    
    Returns:
        float: Breathing Loss (API bbl)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 1, Page: 123.
    """
    b = (pressure / 14.5) * (tank_diameter**1.8) * paint_factor * outage_factor
    return b


def column_diameter_packed_towers(
    mass_flow_rate: float,
    gas_mass_flow_rate: float
) -> float:
    """
    Calculate column diameter of packed towers.
    
    Args:
        mass_flow_rate: Mass Flow Rate (lb/s)
        gas_mass_flow_rate: Gas Mass Flow Rate (lb/ft²·h)
    
    Returns:
        float: Column Diameter (ft)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 319.
    """
    d = ((4 * mass_flow_rate) / (math.pi * gas_mass_flow_rate))**0.5
    return d


def cooling_ideal_gas_energy(
    h1: float,
    h2: float,
    v1: float,
    v2: float,
    gravity: float,
    height1: float,
    height2: float
) -> float:
    """
    Calculate energy rate for cooling of an ideal gas.
    
    Args:
        h1: Initial Enthalpy Per Unit Mass (ft²/s²)
        h2: Final Enthalpy Per Unit Mass (ft²/s²)
        v1: Initial Velocity (ft/s)
        v2: Final Velocity (ft/s)
        gravity: Acceleration Due to Gravity (ft/s²)
        height1: Initial Height (ft)
        height2: Final Height (ft)
    
    Returns:
        float: Energy Rate (Btu/s)
    
    Reference:
        Bird, R.B., Stewart, W.E. and Lightfoot, E.N. (2002). Transport Phenomena 
        (Second Ed.). John Wiley & Sons, Chapter: 18, Page: 576.
    """
    q = (h2 - h1) + 0.5 * (v2**2 - v1**2) + gravity * (height2 - height1)
    return q


def correction_factor_foamless_separation(
    length: float,
    diameter: float
) -> float:
    """
    Calculate correction factor for foamless separation.
    
    Args:
        length: Length of Tank (ft)
        diameter: Diameter of Tank (ft)
    
    Returns:
        float: Correction Factor (dimensionless)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 73.
    """
    k = ((length / diameter) / 5)**0.56
    return k


def benedict_webb_rubin_correlation_factor(
    mole_fraction_h2s_co2: float,
    mole_fraction_h2s: float
) -> float:
    """
    Calculate correlation factor for Benedict-Webb-Rubin equation.
    
    Args:
        mole_fraction_h2s_co2: Mole Fraction of H2S and CO2 in Gas Phase (fraction)
        mole_fraction_h2s: Mole Fraction of H2S in Gas Phase (fraction)
    
    Returns:
        float: Correlation Factor (°R)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 1, Page: 54.
    """
    term1 = 120 * (mole_fraction_h2s_co2**0.9 - mole_fraction_h2s_co2**1.6)
    term2 = 15 * (mole_fraction_h2s**0.5 - mole_fraction_h2s**4)
    e = term1 + term2
    return e


def critical_pressure_van_der_waals(
    pseudo_critical_pressure: float,
    pseudo_critical_temp: float,
    critical_temp: float,
    h2s_fraction: float,
    correlation_constant: float
) -> float:
    """
    Calculate critical pressure values for Van Der Waals equation.
    
    Args:
        pseudo_critical_pressure: Pseudocritical Pressure (psi)
        pseudo_critical_temp: Pseudocritical Temperature (°R)
        critical_temp: Critical Temperature (°R)
        h2s_fraction: Mole Fraction of Hydrogen Sulfide (fraction)
        correlation_constant: Correlation Constant (dimensionless)
    
    Returns:
        float: Adjusted Critical Pressure (psi)
    
    Note:
        Applies correction for presence of H2S and other impurities.
    """
    correction = 1 + correlation_constant * h2s_fraction * (critical_temp / pseudo_critical_temp)
    adjusted_pressure = pseudo_critical_pressure * correction
    return adjusted_pressure


def gas_separator_internal_diameter(
    gas_flow_rate: float,
    allowable_velocity: float
) -> float:
    """
    Calculate internal diameter of gas separator.
    
    Args:
        gas_flow_rate: Gas Flow Rate (ft³/s)
        allowable_velocity: Allowable Gas Velocity (ft/s)
    
    Returns:
        float: Internal Diameter (ft)
    
    Note:
        Based on area = flow rate / velocity, diameter = sqrt(4*area/π)
    """
    area = gas_flow_rate / allowable_velocity
    diameter = (4 * area / math.pi)**0.5
    return diameter


def gas_capacity_separator(
    vessel_diameter: float,
    vessel_length: float,
    gas_velocity: float,
    operating_factor: float = 0.8
) -> float:
    """
    Calculate gas capacity of separator.
    
    Args:
        vessel_diameter: Vessel Diameter (ft)
        vessel_length: Vessel Length (ft)
        gas_velocity: Gas Velocity (ft/s)
        operating_factor: Operating Factor (dimensionless), default = 0.8
    
    Returns:
        float: Gas Capacity (ft³/s)
    
    Note:
        Gas capacity based on cross-sectional area and allowable velocity.
    """
    cross_sectional_area = math.pi * (vessel_diameter / 2)**2
    capacity = cross_sectional_area * gas_velocity * operating_factor
    return capacity


def terminal_velocity_separator(
    particle_diameter: float,
    density_particle: float,
    density_fluid: float,
    fluid_viscosity: float,
    drag_coefficient: float = 0.44
) -> float:
    """
    Calculate terminal velocity in a separator.
    
    Args:
        particle_diameter: Particle Diameter (ft)
        density_particle: Particle Density (lb/ft³)
        density_fluid: Fluid Density (lb/ft³)
        fluid_viscosity: Fluid Viscosity (lb/ft·s)
        drag_coefficient: Drag Coefficient (dimensionless), default = 0.44
    
    Returns:
        float: Terminal Velocity (ft/s)
    
    Note:
        Uses Stokes law for spherical particles in viscous flow.
    """
    gravity = 32.174  # ft/s²
    
    # Stokes law for terminal velocity
    vt = math.sqrt((4 * gravity * particle_diameter * (density_particle - density_fluid)) / 
                   (3 * drag_coefficient * density_fluid))
    return vt


def separator_residence_time(
    liquid_volume: float,
    liquid_flow_rate: float
) -> float:
    """
    Calculate residence time in separator.
    
    Args:
        liquid_volume: Liquid Volume in Separator (bbl)
        liquid_flow_rate: Liquid Flow Rate (bbl/d)
    
    Returns:
        float: Residence Time (min)
    
    Note:
        Residence time = Volume / Flow rate
    """
    if liquid_flow_rate == 0:
        return float('inf')
    
    residence_time_days = liquid_volume / liquid_flow_rate
    residence_time_minutes = residence_time_days * 24 * 60  # Convert to minutes
    return residence_time_minutes


def pressure_vessel_wall_thickness_asme(
    internal_pressure: float,
    internal_radius: float,
    allowable_stress: float,
    joint_efficiency: float = 1.0,
    corrosion_allowance: float = 0.125
) -> float:
    """
    Calculate wall thickness criteria for separator by ASME code.
    
    Args:
        internal_pressure: Internal Pressure (psi)
        internal_radius: Internal Radius (in.)
        allowable_stress: Allowable Stress (psi)
        joint_efficiency: Joint Efficiency (dimensionless), default = 1.0
        corrosion_allowance: Corrosion Allowance (in.), default = 0.125
    
    Returns:
        float: Required Wall Thickness (in.)
    
    Reference:
        ASME Boiler and Pressure Vessel Code
    """
    # ASME formula for cylindrical shells under internal pressure
    t_required = (internal_pressure * internal_radius) / (allowable_stress * joint_efficiency - 0.6 * internal_pressure)
    t_total = t_required + corrosion_allowance
    return t_total


def wobbe_index(
    heating_value: float,
    specific_gravity: float
) -> float:
    """
    Calculate Wobbe index for gas interchangeability.
    
    Args:
        heating_value: Higher Heating Value (Btu/ft³)
        specific_gravity: Specific Gravity (air = 1.0)
    
    Returns:
        float: Wobbe Index (Btu/ft³)
    
    Note:
        Wobbe Index = Heating Value / sqrt(Specific Gravity)
        Used to compare interchangeability of fuel gases.
    """
    wobbe = heating_value / math.sqrt(specific_gravity)
    return wobbe


def glycol_dehydration_teg_weight_percent(
    water_content_inlet: float,
    water_content_outlet: float,
    teg_circulation_rate: float
) -> float:
    """
    Calculate TEG weight percent in glycol dehydration unit.
    
    Args:
        water_content_inlet: Water Content Inlet (lb/MMscf)
        water_content_outlet: Water Content Outlet (lb/MMscf)
        teg_circulation_rate: TEG Circulation Rate (gal/lb water removed)
    
    Returns:
        float: TEG Weight Percent (%)
    
    Note:
        Simplified calculation for glycol dehydration design.
    """
    water_removed = water_content_inlet - water_content_outlet
    
    # Typical TEG concentrations range from 98.5% to 99.5%
    # Higher circulation rates allow lower concentrations
    if teg_circulation_rate > 3:
        teg_purity = 98.5 + (teg_circulation_rate - 3) * 0.2
    else:
        teg_purity = 98.5
    
    return min(teg_purity, 99.5)


def refrigeration_temperature_drop(
    inlet_temperature: float,
    inlet_pressure: float,
    outlet_pressure: float,
    joule_thomson_coefficient: float = 0.25
) -> float:
    """
    Calculate temperature after refrigeration/expansion.
    
    Args:
        inlet_temperature: Inlet Temperature (°F)
        inlet_pressure: Inlet Pressure (psia)
        outlet_pressure: Outlet Pressure (psia)
        joule_thomson_coefficient: Joule-Thomson Coefficient (°F/psi), default = 0.25
    
    Returns:
        float: Outlet Temperature (°F)
    
    Note:
        Uses Joule-Thomson effect for gas expansion cooling.
    """
    pressure_drop = inlet_pressure - outlet_pressure
    temperature_drop = joule_thomson_coefficient * pressure_drop
    outlet_temp = inlet_temperature - temperature_drop
    return outlet_temp


def compressor_energy_requirement(
    inlet_pressure: float,
    outlet_pressure: float,
    gas_flow_rate: float,
    compression_ratio: float,
    efficiency: float = 0.8
) -> float:
    """
    Calculate energy requirement of single-stage ideal compressor.
    
    Args:
        inlet_pressure: Inlet Pressure (psia)
        outlet_pressure: Outlet Pressure (psia)
        gas_flow_rate: Gas Flow Rate (MMscf/d)
        compression_ratio: Compression Ratio (dimensionless)
        efficiency: Compressor Efficiency (fraction), default = 0.8
    
    Returns:
        float: Power Requirement (HP)
    
    Note:
        Based on isothermal compression model.
    """
    # Convert flow rate to actual conditions
    actual_flow = gas_flow_rate * 1e6 / (24 * 3600)  # scf/s
    
    # Isothermal power calculation
    power_isothermal = (inlet_pressure * actual_flow * math.log(compression_ratio)) / (144 * 550)  # HP
    
    # Actual power considering efficiency
    actual_power = power_isothermal / efficiency
    
    return actual_power


def electrical_heating_pipe(
    radius: float,
    k_ratio: float,
    length: float,
    desired_temp: float,
    ambient_temp: float,
    thermal_conductivity: float,
    heat_transfer_coeff: float
) -> float:
    """
    Calculate electrical power required for heating a pipe.
    
    Args:
        radius: Outer radius (m)
        k_ratio: Ratio of inner radius to outer radius (dimensionless)
        length: Length (m)
        desired_temp: Desired temperature (K)
        ambient_temp: Ambient air temperature (K)
        thermal_conductivity: Thermal conductivity (W/m·K)
        heat_transfer_coeff: Heat transfer coefficient (W/(m²·K))
    
    Returns:
        float: Electrical power required (Watts)
    
    Reference:
        Bird, R.B., Stewart, W.E. and Lightfoot, E.N. (2002). Transport Phenomena 
        (Second Ed.). John Wiley & Sons, Chapter: 10, Page: 325.
    """
    import math
    
    numerator = math.pi * radius**2 * (1 - k_ratio**2) * length * (desired_temp - ambient_temp)
    
    term1 = (1 - k_ratio**2) * radius / (2 * heat_transfer_coeff)
    term2 = (k_ratio * radius)**2 / (4 * thermal_conductivity)
    term3 = (1 - (1/k_ratio**2)) / 2
    term4 = math.log(k_ratio)
    
    denominator = term1 + term2 * (term3 - term4)
    
    power = numerator / denominator
    return power


def energy_requirement_single_stage_compressor(
    velocity: float,
    initial_pressure: float,
    final_pressure: float,
    gas_constant: float,
    temperature: float,
    mass: float,
    adiabatic_constant: float
) -> float:
    """
    Calculate energy requirement of single-stage ideal compressor.
    
    Args:
        velocity: Velocity (ft/s)
        initial_pressure: Initial pressure (psi)
        final_pressure: Final pressure (psi)
        gas_constant: Ideal gas constant (ft³·lb/mol·K)
        temperature: Temperature (K)
        mass: Mass (lbs)
        adiabatic_constant: Adiabatic constant (dimensionless)
    
    Returns:
        float: Energy requirement (ft·lbf/lbm)
    
    Reference:
        Bird R. Byron, Stewart E. Warren, Lightfoot N. Edward.
    """
    import math
    
    kinetic_term = velocity**2 / 2 * (1 - (initial_pressure / final_pressure)**2)
    
    compression_term = (gas_constant * temperature * adiabatic_constant) / (mass * (adiabatic_constant - 1))
    pressure_ratio = (final_pressure / initial_pressure)**((adiabatic_constant - 1) / adiabatic_constant)
    
    energy = kinetic_term + compression_term * (pressure_ratio - 1)
    return energy


def thermocouple_temperature_error(
    indicated_temp: float,
    wall_temp: float,
    heat_conduction_constant: float,
    length: float,
    thermal_conductivity: float,
    breadth: float
) -> float:
    """
    Calculate actual thermocouple temperature accounting for conduction error.
    
    Args:
        indicated_temp: Temperature indicated by thermocouple (K)
        wall_temp: Temperature of wall (K)
        heat_conduction_constant: Heat conduction constant (dimensionless)
        length: Length (cm)
        thermal_conductivity: Thermal conductivity (W/m·K)
        breadth: Breadth (cm)
    
    Returns:
        float: Actual thermocouple temperature (K)
    
    Reference:
        Bird, R.B., Stewart, W.E. and Lightfoot, E.N. (2002). Transport Phenomena 
        (Second Ed.). John Wiley & Sons, Chapter: 10, Page: 310.
    """
    import math
    
    # Calculate correction factor n
    cosh_arg = heat_conduction_constant * (length**2 / (thermal_conductivity * breadth))**0.5
    n = 1 / math.cosh(cosh_arg)
    
    # Calculate actual temperature
    actual_temp = (indicated_temp - n * wall_temp) / (1 - n)
    return actual_temp


def eykman_molecular_refraction(
    vapor_pressure: float,
    pressure: float,
    fugacity_vapor: float,
    fugacity_pressure: float
) -> float:
    """
    Calculate Eykman molecular refraction constant.
    
    Args:
        vapor_pressure: Vapor pressure of water (psi)
        pressure: System pressure (psi)
        fugacity_vapor: Fugacity of water at vapor pressure (dimensionless)
        fugacity_pressure: Fugacity of water at system pressure (dimensionless)
    
    Returns:
        float: Eykman constant (dimensionless)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 1, Page: 50.
    """
    term1 = vapor_pressure / pressure
    term2 = (fugacity_vapor / vapor_pressure) / (fugacity_pressure / vapor_pressure)
    term3 = ((pressure - vapor_pressure) / vapor_pressure)**0.049
    
    k = term1 * term2 * term3
    return k


def fenske_minimum_theoretical_plates(
    distillate_light_fraction: float,
    distillate_heavy_fraction: float,
    bottom_light_fraction: float,
    bottom_heavy_fraction: float,
    relative_volatility: float
) -> float:
    """
    Calculate minimum theoretical plates using Fenske's method.
    
    Args:
        distillate_light_fraction: Distillate mole fraction of light component (fraction)
        distillate_heavy_fraction: Distillate mole fraction of heavy component (fraction)
        bottom_light_fraction: Bottom mole fraction of light component (fraction)
        bottom_heavy_fraction: Bottom mole fraction of heavy component (fraction)
        relative_volatility: Relative volatility (fraction)
    
    Returns:
        float: Number of minimum theoretical stages (dimensionless)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 288.
    """
    import math
    
    numerator = (distillate_light_fraction / distillate_heavy_fraction) * (bottom_light_fraction / bottom_heavy_fraction)
    sm = math.log(numerator) / math.log(relative_volatility)
    return sm


def gas_mass_velocity_adsorption(
    gas_velocity: float,
    specific_gravity: float,
    pressure: float,
    temperature: float,
    compressibility: float
) -> float:
    """
    Calculate gas mass velocity in an adsorption unit.
    
    Args:
        gas_velocity: Gas velocity (ft/min)
        specific_gravity: Specific gravity of gas (dimensionless)
        pressure: Pressure (psi)
        temperature: Inlet gas temperature (K)
        compressibility: Compressibility factor (dimensionless)
    
    Returns:
        float: Gas mass velocity (lb/h·ft²)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 391.
    """
    w = (162 * gas_velocity * specific_gravity * pressure) / (temperature * compressibility)
    return w


def gas_mass_velocity_separator_flow(
    mass_velocity: float,
    diameter: float,
    gas_fraction: float
) -> float:
    """
    Calculate mass rate from gas mass velocity in separator.
    
    Args:
        mass_velocity: Mass flow velocity (lb/h·ft²)
        diameter: Internal diameter of separator (ft)
        gas_fraction: Fraction of area available for gas (fraction)
    
    Returns:
        float: Mass rate (lb/h)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 75.
    """
    mass_rate = 0.785 * mass_velocity * diameter**2 * gas_fraction
    return mass_rate


def gas_originally_adsorbed(
    drainage_area: float,
    thickness: float,
    bulk_density: float,
    gas_content: float
) -> float:
    """
    Calculate gas originally adsorbed in coalbed methane reservoir.
    
    Args:
        drainage_area: Drainage area (acres)
        thickness: Thickness (ft)
        bulk_density: Bulk density of coal (g/cc)
        gas_content: Gas content (scf/ton)
    
    Returns:
        float: Gas initially in place (scf)
    
    Reference:
        Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
        Gulf Publishing of Elsevier, Chapter: 3, Page: 227.
    """
    gas_in_place = 1359.7 * drainage_area * thickness * bulk_density * gas_content
    return gas_in_place


def gas_pressure_testing_time(
    pipe_diameter: float,
    pipe_length: float,
    initial_pressure: float
) -> float:
    """
    Calculate minimum time needed for gas pressure testing.
    
    Args:
        pipe_diameter: Internal pipe diameter (in.)
        pipe_length: Length of pipe (miles)
        initial_pressure: Initial pressure (psi)
    
    Returns:
        float: Minimum time needed for testing (h)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 30.
    """
    test_time = (3 * pipe_diameter**2 * pipe_length) / initial_pressure
    return test_time


def gravitational_attraction_bouguer(
    gravitational_constant: float,
    thickness: float,
    density_contrast: float
) -> float:
    """
    Calculate gravitational attraction of a layer (Bouguer correction).
    
    Args:
        gravitational_constant: Gravitational constant (N·m²/kg²)
        thickness: Thickness (m)
        density_contrast: Density contrast (kg/m³)
    
    Returns:
        float: Bouguer gravity (m/s²)
    
    Reference:
        https://sites.ualberta.ca/~unsworth/UA-classes/210/exams210/210-final-2008-formula-sheet.pdf
    """
    import math
    
    bouguer_gravity = 2 * math.pi * gravitational_constant * thickness * density_contrast
    return bouguer_gravity


def heating_liquid_agitated_tank(
    initial_temp: float,
    steam_temp: float,
    heat_coefficient: float,
    area: float,
    weight: float,
    specific_heat: float,
    time: float
) -> float:
    """
    Calculate final temperature of liquid heated in agitated tank.
    
    Args:
        initial_temp: Initial temperature (K)
        steam_temp: Steam temperature (K)
        heat_coefficient: Heat coefficient (W/ft·K)
        area: Area (ft²)
        weight: Weight (lbm)
        specific_heat: Specific heat of mass (lbf/lbs·K)
        time: Time (h)
    
    Returns:
        float: Final temperature (K)
    
    Reference:
        Bird, R.B., Stewart, W.E. and Lightfoot, E.N. (2002). Transport Phenomena 
        (Second Ed.). John Wiley & Sons, Chapter: 15, Page: 468.
    """
    import math
    
    ua_over_wcp = (heat_coefficient * area) / (weight * specific_heat)
    exponential_term = 1 - math.exp(-ua_over_wcp * time)
    
    final_temp = initial_temp + (steam_temp - initial_temp) * exponential_term
    return final_temp


def height_downcomer_filling(
    clear_liquid_height: float,
    dry_tray_height: float,
    head_loss_downcomer: float,
    liquid_density: float,
    gas_density: float,
    tray_inlet_head: float
) -> float:
    """
    Calculate height of downcomer filling in tray tower.
    
    Args:
        clear_liquid_height: Clear liquid height (in.)
        dry_tray_height: Dry tray height (in.)
        head_loss_downcomer: Head loss under downcomer (in.)
        liquid_density: Liquid density (g/cc)
        gas_density: Gas density (g/cc)
        tray_inlet_head: Tray inlet head (in.)
    
    Returns:
        float: Height of downcomer filling (in.)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 316.
    """
    density_ratio = liquid_density / (liquid_density - gas_density)
    height = (clear_liquid_height + dry_tray_height + head_loss_downcomer) * density_ratio + tray_inlet_head + 1
    return height


def inhibitor_injection_rate(
    water_mass: float,
    rich_concentration: float,
    lean_concentration: float
) -> float:
    """
    Calculate inhibitor injection rate required.
    
    Args:
        water_mass: Mass of water (lb)
        rich_concentration: Rich inhibitor concentration (wt%)
        lean_concentration: Lean inhibitor concentration (wt%)
    
    Returns:
        float: Mass of inhibitor required (lb)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 1, Page: 181.
    """
    inhibitor_mass = water_mass * (rich_concentration / (lean_concentration - rich_concentration))
    return inhibitor_mass


def instrumentation_noise_control(
    measured_pressure: float,
    reference_pressure: float
) -> float:
    """
    Calculate noise level in decibels.
    
    Args:
        measured_pressure: Pressure of sound measured (psi)
        reference_pressure: Reference pressure (psi)
    
    Returns:
        float: Decibel level (dB)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 1, Page: 297.
    """
    import math
    
    decibels = 20 * math.log10(measured_pressure / reference_pressure)
    return decibels


def isostacy_airy_hypothesis(
    mountain_height: float,
    crustal_density: float,
    mantle_density: float
) -> float:
    """
    Calculate root depth using Airy hypothesis of isostacy.
    
    Args:
        mountain_height: Mountain height (m)
        crustal_density: Crustal density (kg/m³)
        mantle_density: Mantle density (kg/m³)
    
    Returns:
        float: Root depth (m)
    
    Reference:
        https://sites.ualberta.ca/~unsworth/UA-classes/210/exams210/210-final-2008-formula-sheet.pdf
    """
    root_depth = mountain_height * (crustal_density / (mantle_density - crustal_density))
    return root_depth


def lift_coefficient(
    density: float,
    velocity: float,
    lift_force: float,
    planform_area: float
) -> float:
    """
    Calculate lift coefficient for aerodynamic analysis.
    
    Args:
        density: Density (kg/m³)
        velocity: True air speed (m/s)
        lift_force: Lift force (Newton)
        planform_area: Planform area (m²)
    
    Returns:
        float: Lift coefficient (dimensionless)
    
    Reference:
        Wikipedia.org
    """
    lift_coeff = (2 * lift_force) / (density * velocity**2 * planform_area)
    return lift_coeff


def mass_steel_shell_adsorption(
    vessel_length: float,
    vessel_diameter: float,
    shell_thickness: float
) -> float:
    """
    Calculate mass of steel shell in adsorption unit.
    
    Args:
        vessel_length: Vessel length (ft)
        vessel_diameter: Vessel internal diameter (in.)
        shell_thickness: Shell thickness (in.)
    
    Returns:
        float: Mass of steel shell (lb)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Vol. 2, Page: 398, 
        Campbell Petroleum Series, Oklahoma, 1992.
    """
    mass = 15 * vessel_length * vessel_diameter * shell_thickness
    return mass


def mass_transfer_zone_length(
    water_loading: float,
    gas_velocity: float,
    relative_saturation: float
) -> float:
    """
    Calculate mass transfer zone length of adsorption unit.
    
    Args:
        water_loading: Water loading (lb/ft²·h)
        gas_velocity: Velocity (ft/min)
        relative_saturation: Relative saturation of inlet gas (%)
    
    Returns:
        float: Mass transfer zone length (ft)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 390.
    """
    mtz_length = (375 * water_loading**0.7895) / (gas_velocity**0.5506 * relative_saturation**0.2646)
    return mtz_length


def modified_clapeyron_criteria(
    component_constant: float
) -> float:
    """
    Calculate hydrate forming temperature using modified Clapeyron criteria.
    
    Args:
        component_constant: Component constant for hydrocarbon levels to pressure (K)
    
    Returns:
        float: Hydrate forming temperature (°R)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 1, Page: 178.
    """
    temperature = 3.89 * (component_constant**0.5)
    return temperature


def packed_column_actual_height(
    height_transfer_unit: float,
    number_transfer_units: float
) -> float:
    """
    Calculate actual height of packed column.
    
    Args:
        height_transfer_unit: Height of a transfer unit (ft)
        number_transfer_units: Number of transfer units (dimensionless)
    
    Returns:
        float: Height of column (ft)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Campbell Petroleum Series, 
        Oklahoma, 1992, Vol. 2, Page: 280.
    """
    column_height = height_transfer_unit * number_transfer_units
    return column_height


def pan_maddox_molecular_weight(
    boiling_temperature: float,
    relative_density: float
) -> float:
    """
    Calculate molecular weight using Pan-Maddox equation.
    
    Args:
        boiling_temperature: Boiling temperature (K)
        relative_density: Relative density at 15.5°C (g/cc)
    
    Returns:
        float: Molecular weight (g/mol)
    
    Reference:
        John M. Campbell, Gas Conditioning and Processing, Vol. 1, Page: 76, 
        Campbell Petroleum Series, Oklahoma, 1992.
    """
    molecular_weight = 1.66e-4 * (boiling_temperature**2.2) * (relative_density**-1.02)
    return molecular_weight


def photoelectric_effect_velocity(
    rest_mass: float,
    kinetic_energy: float,
    light_velocity: float = 3e8
) -> float:
    """
    Calculate particle velocity from photoelectric effect.
    
    Args:
        rest_mass: Mass of body at rest (kg)
        kinetic_energy: Kinetic energy (Joule)
        light_velocity: Velocity of light (m/s), default = 3e8
    
    Returns:
        float: Velocity of particle (m/s)
    
    Reference:
        Bassiouni, Z., 1994, Theory, Measurement, and interpretation of Well Logs. 
        SPE Textbook Series Vol. 4. Chapter 2, Page: 33.
    """
    import math
    
    relativistic_factor = 1 + (kinetic_energy / (rest_mass * light_velocity**2))
    velocity = light_velocity * (1 - (1 / relativistic_factor**2))**0.5
    return velocity


def power_pumping_compressible_fluid(
    pipe_diameter: float,
    pressure: float,
    mass: float,
    gas_constant: float,
    temperature: float,
    compressor_energy: float,
    velocity: float
) -> float:
    """
    Calculate power requirement for pumping compressible flow fluid through long pipe.
    
    Args:
        pipe_diameter: Diameter of pipe (ft)
        pressure: Pressure (psi)
        mass: Mass (lbs)
        gas_constant: Gas constant (ft³·psi/lbmol·K)
        temperature: Temperature (K)
        compressor_energy: Energy required by compressor (ft·lbf/lbm)
        velocity: Velocity (ft/s)
    
    Returns:
        float: Power requirement (hp)
    
    Reference:
        Bird, R.B., Stewart, W.E. and Lightfoot, E.N. (2002). Transport Phenomena 
        (Second Ed.). John Wiley & Sons, Chapter: 15, Page: 465.
    """
    import math
    
    cross_sectional_area = math.pi * pipe_diameter**2 / 4
    power = (velocity * cross_sectional_area * pressure * mass * compressor_energy) / (4 * gas_constant * temperature)
    return power
