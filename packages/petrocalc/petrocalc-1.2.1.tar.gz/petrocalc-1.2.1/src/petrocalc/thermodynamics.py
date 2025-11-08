"""
Thermodynamics calculations for petroleum engineering.

This module contains functions for thermodynamic calculations including:
- Heat transfer calculations
- Phase behavior
- Thermal properties
- Temperature and heat balance calculations
"""

import math
from typing import Union, Tuple, Optional


def heat_capacity_oil(
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates heat capacity of crude oil.
    
    Args:
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        
    Returns:
        float: Heat capacity in Btu/lb-°F
    """
    api = oil_gravity
    t = temperature
    
    # Watson and Nelson correlation
    specific_gravity = 141.5 / (api + 131.5)
    k = (1.8 * specific_gravity)**0.5
    
    cp = (0.388 + 0.00045 * t) / math.sqrt(specific_gravity)
    
    return cp


def heat_capacity_gas(
    gas_gravity: float,
    temperature: float,
    pressure: float = 14.7
) -> float:
    """
    Calculates heat capacity of natural gas at constant pressure.
    
    Args:
        gas_gravity (float): Gas specific gravity (air = 1.0)
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia (default 14.7)
        
    Returns:
        float: Heat capacity in Btu/lb-°F
    """
    sg = gas_gravity
    t = temperature + 459.67  # Convert to °R
    p = pressure
    
    # Correlation for natural gas
    cp = 0.031 + 0.0000154 * t - 5.3e-9 * t**2
    
    # Pressure correction (simplified)
    cp = cp * (1 + 0.0001 * (p - 14.7))
    
    return cp


def heat_capacity_water(temperature: float, pressure: float = 14.7) -> float:
    """
    Calculates heat capacity of water.
    
    Args:
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia (default 14.7)
        
    Returns:
        float: Heat capacity in Btu/lb-°F
    """
    t = temperature
    
    # Correlation for liquid water
    cp = 1.0 - 0.0001 * (t - 32) + 0.0000002 * (t - 32)**2
    
    return cp


def thermal_conductivity_oil(
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates thermal conductivity of crude oil.
    
    Args:
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        
    Returns:
        float: Thermal conductivity in Btu/hr-ft-°F
    """
    api = oil_gravity
    t = temperature
    
    # Cragoe correlation
    specific_gravity = 141.5 / (api + 131.5)
    k = 0.08 - 0.0003 * (t - 32) - 0.02 * specific_gravity
    
    return max(0.05, k)  # Minimum practical value


def thermal_conductivity_gas(
    gas_gravity: float,
    temperature: float,
    pressure: float = 14.7
) -> float:
    """
    Calculates thermal conductivity of natural gas.
    
    Args:
        gas_gravity (float): Gas specific gravity (air = 1.0)
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia (default 14.7)
        
    Returns:
        float: Thermal conductivity in Btu/hr-ft-°F
    """
    sg = gas_gravity
    t = temperature + 459.67  # Convert to °R
    
    # Correlation for natural gas
    k = 0.00154 * (t / 530)**0.79 / sg**0.5
    
    return k


def thermal_expansion_coefficient_oil(
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates thermal expansion coefficient of oil.
    
    Args:
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        
    Returns:
        float: Thermal expansion coefficient in 1/°F
    """
    api = oil_gravity
    t = temperature
    
    # Standing correlation
    beta = (0.00036 + 0.000055 * api) * (1 + 0.0004 * (t - 60))
    
    return beta


def heat_transfer_coefficient_forced_convection(
    velocity: float,
    pipe_diameter: float,
    fluid_density: float,
    fluid_viscosity: float,
    thermal_conductivity: float,
    heat_capacity: float
) -> float:
    """
    Calculates heat transfer coefficient for forced convection in pipes.
    
    Args:
        velocity (float): Fluid velocity in ft/sec
        pipe_diameter (float): Pipe diameter in ft
        fluid_density (float): Fluid density in lb/ft³
        fluid_viscosity (float): Fluid viscosity in cp
        thermal_conductivity (float): Thermal conductivity in Btu/hr-ft-°F
        heat_capacity (float): Heat capacity in Btu/lb-°F
        
    Returns:
        float: Heat transfer coefficient in Btu/hr-ft²-°F
    """
    v = velocity
    d = pipe_diameter
    rho = fluid_density
    mu = fluid_viscosity * 2.42  # Convert cp to lb/hr-ft
    k = thermal_conductivity
    cp = heat_capacity
    
    # Reynolds number
    re = rho * v * d * 3600 / mu  # 3600 to convert velocity units
    
    # Prandtl number
    pr = cp * mu / k
    
    # Nusselt number (Dittus-Boelter equation)
    if re > 10000:
        nu = 0.023 * re**0.8 * pr**0.4
    else:
        # Laminar flow
        nu = 3.66
    
    # Heat transfer coefficient
    h = nu * k / d
    
    return h


def heat_loss_insulated_pipe(
    inner_temperature: float,
    outer_temperature: float,
    pipe_inner_radius: float,
    pipe_outer_radius: float,
    insulation_outer_radius: float,
    pipe_thermal_conductivity: float,
    insulation_thermal_conductivity: float,
    length: float
) -> float:
    """
    Calculates heat loss from insulated pipe.
    
    Args:
        inner_temperature (float): Inner fluid temperature in °F
        outer_temperature (float): Ambient temperature in °F
        pipe_inner_radius (float): Pipe inner radius in ft
        pipe_outer_radius (float): Pipe outer radius in ft
        insulation_outer_radius (float): Insulation outer radius in ft
        pipe_thermal_conductivity (float): Pipe thermal conductivity in Btu/hr-ft-°F
        insulation_thermal_conductivity (float): Insulation thermal conductivity in Btu/hr-ft-°F
        length (float): Pipe length in ft
        
    Returns:
        float: Heat loss in Btu/hr
    """
    t_inner = inner_temperature
    t_outer = outer_temperature
    r1 = pipe_inner_radius
    r2 = pipe_outer_radius
    r3 = insulation_outer_radius
    k_pipe = pipe_thermal_conductivity
    k_insul = insulation_thermal_conductivity
    l = length
    
    # Thermal resistances
    r_pipe = math.log(r2 / r1) / (2 * math.pi * k_pipe * l)
    r_insul = math.log(r3 / r2) / (2 * math.pi * k_insul * l)
    
    # Total thermal resistance
    r_total = r_pipe + r_insul
    
    # Heat loss
    q = (t_inner - t_outer) / r_total
    
    return q


def temperature_drop_flowing_well(
    depth: float,
    flow_rate: float,
    geothermal_gradient: float = 0.015,
    surface_temperature: float = 70
) -> float:
    """
    Calculates temperature at depth in flowing well.
    
    Args:
        depth (float): Depth in ft
        flow_rate (float): Flow rate in bbl/day
        geothermal_gradient (float): Geothermal gradient in °F/ft (default 0.015)
        surface_temperature (float): Surface temperature in °F (default 70)
        
    Returns:
        float: Temperature at depth in °F
    """
    d = depth
    q = flow_rate
    grad = geothermal_gradient
    t_surf = surface_temperature
    
    # Static temperature
    t_static = t_surf + grad * d
    
    # Flowing temperature (simplified - assumes cooling due to expansion)
    cooling_factor = 1 - 0.0001 * math.sqrt(q)  # Simplified correlation
    t_flowing = t_static * cooling_factor
    
    return t_flowing


def joule_thomson_coefficient_gas(
    temperature: float,
    pressure: float,
    gas_gravity: float
) -> float:
    """
    Calculates Joule-Thomson coefficient for natural gas.
    
    Args:
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        gas_gravity (float): Gas specific gravity (air = 1.0)
        
    Returns:
        float: Joule-Thomson coefficient in °F/psi
    """
    t = temperature + 459.67  # Convert to °R
    p = pressure
    sg = gas_gravity
    
    # Calculate reduced properties
    tc = 168 + 325 * sg - 12.5 * sg**2  # Critical temperature in °R
    pc = 677 + 15.0 * sg - 37.5 * sg**2  # Critical pressure in psia
    
    tr = t / tc
    pr = p / pc
    
    # Simplified correlation
    jt = (5.4 - 17.5 * tr + 8.7 * tr**2) / (pc * (1 + 0.1 * pr))
    
    return jt


def heat_of_vaporization_oil(
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates heat of vaporization for crude oil.
    
    Args:
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        
    Returns:
        float: Heat of vaporization in Btu/lb
    """
    api = oil_gravity
    t = temperature + 459.67  # Convert to °R
    
    # Watson correlation
    specific_gravity = 141.5 / (api + 131.5)
    
    # Critical temperature estimate
    tc = 1166 - 3 * api  # °R
    
    # Reduced temperature
    tr = t / tc
    
    if tr >= 1.0:
        return 0  # Above critical temperature
    
    # Heat of vaporization
    hv = 8.314 * tc * (1 - tr)**0.38 / (28.97 * specific_gravity)
    
    return hv


def bubble_point_temperature(
    pressure: float,
    oil_gravity: float,
    gas_gravity: float,
    gas_oil_ratio: float
) -> float:
    """
    Calculates bubble point temperature.
    
    Args:
        pressure (float): Pressure in psia
        oil_gravity (float): Oil API gravity in degrees
        gas_gravity (float): Gas specific gravity (air = 1.0)
        gas_oil_ratio (float): Gas-oil ratio in scf/STB
        
    Returns:
        float: Bubble point temperature in °F
    """
    p = pressure
    api = oil_gravity
    sg = gas_gravity
    gor = gas_oil_ratio
    
    # Standing's correlation (rearranged for temperature)
    # Simplified iteration approach
    t_guess = 150  # Initial guess
    
    for _ in range(10):  # Simple iteration
        rs_calc = sg * ((p / 18.2) + 1.4) * (10**(0.0125 * api - 0.00091 * t_guess))
        
        if abs(rs_calc - gor) < 1:
            break
        
        # Adjust temperature
        if rs_calc > gor:
            t_guess -= 5
        else:
            t_guess += 5
    
    return t_guess

# =============================================================================
# CHAPTER 8: PHASE BEHAVIOR AND THERMODYNAMICS FORMULAS
# =============================================================================

def amount_of_heat_required_temperature_increase(
    reservoir_volume_acre_ft: float,
    volumetric_heat_capacity: float,
    initial_temperature: float,
    final_temperature: float
) -> float:
    """
    Calculate amount of heat required to increase reservoir temperature.
    
    Args:
        reservoir_volume_acre_ft (float): Volume of reservoir (acre ft)
        volumetric_heat_capacity (float): Volumetric heat capacity of reservoir (BTU/ft³°F)
        initial_temperature (float): Initial temperature in K
        final_temperature (float): Final temperature in K
        
    Returns:
        float: Amount of heat required to increase temperature (BTU)
    """
    if reservoir_volume_acre_ft < 0:
        raise ValueError("Reservoir volume must be non-negative")
    if volumetric_heat_capacity < 0:
        raise ValueError("Heat capacity must be non-negative")
    if final_temperature <= initial_temperature:
        raise ValueError("Final temperature must be greater than initial temperature")
    
    return 43560 * reservoir_volume_acre_ft * volumetric_heat_capacity * (final_temperature - initial_temperature)


def benedict_webb_rubin_pvt(
    gas_constant: float,
    temperature: float,
    density: float,
    A: float, B: float, C: float,
    a: float, b: float, c: float,
    alpha: float, gamma: float
) -> float:
    """
    Calculate pressure using Benedict-Webb-Rubin equation of state.
    
    Args:
        gas_constant (float): Gas constant (BTU/mol·psi·K)
        temperature (float): Temperature (K)
        density (float): Density (g/cc)
        A, B, C, a, b, c, alpha, gamma (float): Correlation constants
        
    Returns:
        float: Pressure (psi)
    """
    if temperature <= 0:
        raise ValueError("Temperature must be positive")
    if density < 0:
        raise ValueError("Density must be non-negative")
    
    R, T, rho = gas_constant, temperature, density
    
    term1 = R * T * rho
    term2 = (B * R * T - A - C / T**2) * rho**2
    term3 = rho**3 * (b * R * T - a)
    term4 = alpha * a * rho**6
    term5 = c * rho**3 / T**2 * (1 + gamma * rho**2) * math.exp(-gamma * rho**2)
    
    return term1 + term2 + term3 + term4 + term5


def critical_pressure_cavett(
    boiling_point_f: float,
    api_gravity: float
) -> float:
    """
    Calculate critical pressure using Cavett relation.
    
    Args:
        boiling_point_f (float): Boiling point temperature (°F)
        api_gravity (float): API gravity of oil (API)
        
    Returns:
        float: Critical pressure (psi)
    """
    if boiling_point_f < 0:
        raise ValueError("Boiling point must be positive")
    if api_gravity < 0:
        raise ValueError("API gravity must be positive")
    
    Tb = boiling_point_f
    API = api_gravity
    
    pc = (10**(2.829 + 0.0009112 * Tb - 0.0000030175 * Tb**2 + 
              0.0000000015141 * Tb**3 - 0.000020876 * Tb * API + 
              0.000000011048 * Tb**2 * API + 
              0.0000000001395 * Tb**2 * API))
    
    return pc


def critical_temperature_cavett(
    boiling_point_f: float,
    api_gravity: float
) -> float:
    """
    Calculate critical temperature using Cavett method.
    
    Args:
        boiling_point_f (float): Boiling point temperature (°F)
        api_gravity (float): API gravity (API)
        
    Returns:
        float: Critical temperature (°F)
    """
    if boiling_point_f < 0:
        raise ValueError("Boiling point must be positive")
    if api_gravity < 0:
        raise ValueError("API gravity must be positive")
    
    Tb = boiling_point_f
    API = api_gravity
    
    tc = (768.071 + 1.7134 * Tb - 0.0010834 * Tb**2 + 
          0.0000003889 * Tb**3 - 0.00089213 * Tb * API + 
          0.00000053095 * Tb**2 * API + 
          0.000000032712 * Tb**2 * API**2)
    
    return tc


def effective_thermal_conductivity_composite_solids(
    continuous_phase_conductivity: float,
    embedded_phase_conductivity: float,
    porosity: float
) -> float:
    """
    Calculate effective thermal conductivity of composite solids.
    
    Args:
        continuous_phase_conductivity (float): Thermal conductivity of continuous phase (W/m·K)
        embedded_phase_conductivity (float): Thermal conductivity of embedded phase (W/m·K)
        porosity (float): Porosity (fraction)
        
    Returns:
        float: Effective thermal conductivity (W/m·K)
    """
    if continuous_phase_conductivity < 0 or embedded_phase_conductivity < 0:
        raise ValueError("Thermal conductivities must be non-negative")
    if not 0 <= porosity <= 1:
        raise ValueError("Porosity must be between 0 and 1")
    
    k0, k1, phi = continuous_phase_conductivity, embedded_phase_conductivity, porosity
    
    if k1 == k0:
        return k0
    
    numerator = 3 * phi * (k1 + 2 * k0) / (k1 - k0) - phi
    denominator = (k1 + 2 * k0) / (k1 - k0) - phi
    
    return k0 * (1 + numerator / denominator)


def einstein_equation_effective_viscosity(
    suspending_medium_viscosity: float,
    volume_fraction_spheres: float
) -> float:
    """
    Calculate effective viscosity using Einstein equation.
    
    Args:
        suspending_medium_viscosity (float): Viscosity of suspending medium (g/cm·s)
        volume_fraction_spheres (float): Volume fraction of spheres (porosity)
        
    Returns:
        float: Effective viscosity (g/cm·s)
    """
    if suspending_medium_viscosity < 0:
        raise ValueError("Viscosity must be non-negative")
    if not 0 <= volume_fraction_spheres <= 1:
        raise ValueError("Volume fraction must be between 0 and 1")
    
    return suspending_medium_viscosity * (1 + 5/2 * volume_fraction_spheres)


def equilibrium_vaporization_ratio(
    vapor_mole_fraction: float,
    liquid_mole_fraction: float
) -> float:
    """
    Calculate equilibrium vaporization ratio (K-value).
    
    Args:
        vapor_mole_fraction (float): Mole fraction of component in vapor phase
        liquid_mole_fraction (float): Mole fraction of component in liquid phase
        
    Returns:
        float: Equilibrium vaporization ratio (dimensionless)
    """
    if not 0 <= vapor_mole_fraction <= 1:
        raise ValueError("Vapor mole fraction must be between 0 and 1")
    if not 0 <= liquid_mole_fraction <= 1:
        raise ValueError("Liquid mole fraction must be between 0 and 1")
    if liquid_mole_fraction == 0:
        raise ValueError("Liquid mole fraction cannot be zero")
    
    return vapor_mole_fraction / liquid_mole_fraction


def equilibrium_vaporization_ratio_heptane(
    heptane_k_value: float,
    ethane_k_value: float,
    constant_b: float
) -> float:
    """
    Calculate equilibrium vaporization ratio of heptane.
    
    Args:
        heptane_k_value (float): Heptane K-value (fraction)
        ethane_k_value (float): Ethane K-value (fraction)
        constant_b (float): Constant (dimensionless)
        
    Returns:
        float: Equilibrium vaporization ratio (fraction)
    """
    if heptane_k_value <= 0 or ethane_k_value <= 0:
        raise ValueError("K-values must be positive")
    
    return (heptane_k_value / ethane_k_value)**constant_b * heptane_k_value


def evaporation_loss_oxygen_tank(
    inner_diameter: float,
    outer_diameter: float,
    inner_temperature: float,
    outer_temperature: float,
    inner_conductivity: float,
    outer_conductivity: float
) -> float:
    """
    Calculate evaporation loss from an oxygen tank.
    
    Args:
        inner_diameter (float): Inner diameter (m)
        outer_diameter (float): Outer diameter (m)
        inner_temperature (float): Inner layer temperature (K)
        outer_temperature (float): Outer layer temperature (K)
        inner_conductivity (float): Thermal conductivity of inner layer (W/m·K)
        outer_conductivity (float): Thermal conductivity of outer layer (W/m·K)
        
    Returns:
        float: Flow rate of evaporation (g/s)
    """
    if inner_diameter <= 0 or outer_diameter <= inner_diameter:
        raise ValueError("Invalid diameter values")
    if inner_temperature <= 0 or outer_temperature <= 0:
        raise ValueError("Temperatures must be positive")
    if inner_conductivity < 0 or outer_conductivity < 0:
        raise ValueError("Thermal conductivities must be non-negative")
    
    r0, r1 = inner_diameter / 2, outer_diameter / 2
    T0, T1 = inner_temperature, outer_temperature
    k0, k1 = inner_conductivity, outer_conductivity
    
    return 4 * math.pi * r0 * r1 * (k0 + k1) / 2 * (T0 - T1) / (r1 - r0)


def peng_robinson_pvt_equation(
    temperature: float,
    volume: float,
    gas_constant: float,
    critical_temperature: float,
    critical_pressure: float,
    acentric_factor: float
) -> float:
    """
    Calculate pressure using Peng-Robinson equation of state.
    
    Args:
        temperature (float): Temperature (K)
        volume (float): Molar volume (m³/mol)
        gas_constant (float): Gas constant (J/mol·K)
        critical_temperature (float): Critical temperature (K)
        critical_pressure (float): Critical pressure (Pa)
        acentric_factor (float): Acentric factor (dimensionless)
        
    Returns:
        float: Pressure (Pa)
    """
    if temperature <= 0 or volume <= 0:
        raise ValueError("Temperature and volume must be positive")
    if critical_temperature <= 0 or critical_pressure <= 0:
        raise ValueError("Critical properties must be positive")
    
    R, T, V = gas_constant, temperature, volume
    Tc, Pc, omega = critical_temperature, critical_pressure, acentric_factor
    
    # Calculate parameters
    a = 0.45724 * R**2 * Tc**2 / Pc
    b = 0.07780 * R * Tc / Pc
    
    # Temperature-dependent alpha function
    Tr = T / Tc
    kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
    alpha = (1 + kappa * (1 - math.sqrt(Tr)))**2
    
    # Pressure calculation
    P = R * T / (V - b) - a * alpha / (V**2 + 2*b*V - b**2)
    
    return P


def van_der_waals_pvt_equation(
    temperature: float,
    volume: float,
    gas_constant: float,
    van_der_waals_a: float,
    van_der_waals_b: float
) -> float:
    """
    Calculate pressure using Van der Waals equation of state.
    
    Args:
        temperature (float): Temperature (K)
        volume (float): Molar volume (m³/mol)
        gas_constant (float): Gas constant (J/mol·K)
        van_der_waals_a (float): Van der Waals constant a (Pa·m⁶/mol²)
        van_der_waals_b (float): Van der Waals constant b (m³/mol)
        
    Returns:
        float: Pressure (Pa)
    """
    if temperature <= 0 or volume <= 0:
        raise ValueError("Temperature and volume must be positive")
    if van_der_waals_a < 0 or van_der_waals_b < 0:
        raise ValueError("Van der Waals constants must be non-negative")
    if volume <= van_der_waals_b:
        raise ValueError("Volume must be greater than Van der Waals constant b")
    
    R, T, V = gas_constant, temperature, volume
    a, b = van_der_waals_a, van_der_waals_b
    
    return R * T / (V - b) - a / V**2


def stefan_boltzmann_law(
    temperature: float,
    emissivity: float = 1.0,
    stefan_boltzmann_constant: float = 5.67e-8
) -> float:
    """
    Calculate radiated energy flux using Stefan-Boltzmann law.
    
    Args:
        temperature (float): Surface temperature (K)
        emissivity (float): Surface emissivity (dimensionless, 0-1, default 1.0)
        stefan_boltzmann_constant (float): Stefan-Boltzmann constant (W/m²·K⁴, default 5.67e-8)
        
    Returns:
        float: Radiated energy flux (W/m²)
    """
    if temperature <= 0:
        raise ValueError("Temperature must be positive")
    if not 0 <= emissivity <= 1:
        raise ValueError("Emissivity must be between 0 and 1")
    
    return emissivity * stefan_boltzmann_constant * temperature**4


def wien_displacement_law(
    temperature: float,
    wien_constant: float = 2.898e-3
) -> float:
    """
    Calculate wavelength of maximum emission using Wien's displacement law.
    
    Args:
        temperature (float): Temperature (K)
        wien_constant (float): Wien displacement constant (m·K, default 2.898e-3)
        
    Returns:
        float: Wavelength of maximum emission (m)
    """
    if temperature <= 0:
        raise ValueError("Temperature must be positive")
    
    return wien_constant / temperature


def thermal_diffusivity(
    thermal_conductivity: float,
    density: float,
    specific_heat: float
) -> float:
    """
    Calculate thermal diffusivity.
    
    Args:
        thermal_conductivity (float): Thermal conductivity (W/m·K)
        density (float): Density (kg/m³)
        specific_heat (float): Specific heat capacity (J/kg·K)
        
    Returns:
        float: Thermal diffusivity (m²/s)
    """
    if thermal_conductivity < 0:
        raise ValueError("Thermal conductivity must be non-negative")
    if density <= 0:
        raise ValueError("Density must be positive")
    if specific_heat <= 0:
        raise ValueError("Specific heat must be positive")
    
    return thermal_conductivity / (density * specific_heat)
