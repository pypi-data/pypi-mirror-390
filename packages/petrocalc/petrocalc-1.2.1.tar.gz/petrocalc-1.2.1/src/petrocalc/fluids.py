"""
Fluid properties calculations.

This module contains functions for calculating fluid properties including:
- PVT properties of oil, gas, and water
- Fluid correlations and equations of state
- Phase behavior calculations
- Thermodynamic properties
"""

import math
from typing import Union, Tuple, Optional


def water_formation_volume_factor(
    temperature: float,
    pressure: float,
    salinity: float = 0
) -> float:
    """
    Calculates water formation volume factor.
    
    Args:
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        salinity (float): Water salinity in ppm (default 0 for fresh water)
        
    Returns:
        float: Water formation volume factor in res bbl/STB
    """
    t = temperature
    p = pressure
    s = salinity / 1000000  # Convert ppm to fraction
    
    # McCain correlation
    dvwt = -1.0001e-2 + 1.33391e-4 * t + 5.50654e-7 * t**2
    dvwp = -1.95301e-9 * p * t - 1.72834e-13 * p**2 * t - 3.58922e-7 * p - 2.25341e-10 * p**2
    dvws = s * (0.0816 - 0.0122 * s + 0.000128 * s**2)
    
    bw = 1 + dvwt + dvwp + dvws
    return bw


def water_compressibility(
    temperature: float,
    pressure: float,
    salinity: float = 0
) -> float:
    """
    Calculates water compressibility.
    
    Args:
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        salinity (float): Water salinity in ppm (default 0)
        
    Returns:
        float: Water compressibility in 1/psi
    """
    t = temperature
    p = pressure
    s = salinity / 1000000  # Convert to fraction
    
    # Osif correlation
    cw = (1 / (7.033 * p + 541.5 * s - 537.0 * t + 403300)) * 1e-6
    return cw


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


def water_viscosity(temperature: float, pressure: float, salinity: float = 0) -> float:
    """
    Calculates water viscosity.
    
    Args:
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        salinity (float): Water salinity in ppm (default 0)
        
    Returns:
        float: Water viscosity in cp
    """
    t = temperature
    p = pressure
    s = salinity / 1000000  # Convert to fraction
    
    # McCain correlation for fresh water viscosity
    # Adjusted correlation to ensure positive values
    if t < 32:
        t = 32  # Prevent calculations below freezing
    
    # Simplified correlation for water viscosity
    mu_w = 1.0 - 0.0035 * (t - 32) + 0.000005 * (t - 32)**2
    
    # Ensure minimum viscosity
    mu_w = max(0.1, mu_w)
    
    # Salinity correction
    if s > 0:
        salinity_factor = 1 + s * 10  # Simplified salinity effect
        mu_w = mu_w * salinity_factor
    
    # Pressure correction (simplified)
    mu_w = mu_w * (1 + 0.000001 * (p - 14.7))
    
    return mu_w


def gas_compressibility_factor_standing(
    pressure: float,
    temperature: float,
    gas_gravity: float
) -> float:
    """
    Calculates gas compressibility factor using Standing-Katz correlation.
    
    Args:
        pressure (float): Pressure in psia
        temperature (float): Temperature in °R
        gas_gravity (float): Gas specific gravity (air = 1.0)
        
    Returns:
        float: Gas compressibility factor (dimensionless)
    """
    sg = gas_gravity
    t = temperature
    p = pressure
    
    # Calculate pseudocritical properties
    tpc = 168 + 325 * sg - 12.5 * sg**2  # °R
    ppc = 677 + 15.0 * sg - 37.5 * sg**2  # psia
    
    # Calculate pseudoreduced properties
    tpr = t / tpc
    ppr = p / ppc
    
    # Standing-Katz correlation (simplified approximation)
    a = 1.39 * (tpr - 0.92)**0.5 - 0.36 * tpr - 0.101
    b = (0.62 - 0.23 * tpr) * ppr + ((0.066 / (tpr - 0.86)) - 0.037) * ppr**2 + (0.32 * ppr**6) / (10**(9 * (tpr - 1)))
    c = 0.132 - 0.32 * math.log10(tpr)
    d = 10**(0.3106 - 0.49 * tpr + 0.1824 * tpr**2)
    
    z = a + (1 - a) / math.exp(b) + c * ppr**d
    
    return max(0.2, min(2.0, z))  # Practical bounds


def gas_density(
    pressure: float,
    temperature: float,
    molecular_weight: float,
    z_factor: float = 1.0
) -> float:
    """
    Calculates gas density using equation of state.
    
    Args:
        pressure (float): Pressure in psia
        temperature (float): Temperature in °R
        molecular_weight (float): Gas molecular weight in lb/lb-mol
        z_factor (float): Gas compressibility factor (dimensionless)
        
    Returns:
        float: Gas density in lb/ft³
    """
    p = pressure
    t = temperature
    mw = molecular_weight
    z = z_factor
    
    # Ideal gas law with compressibility factor
    rho_g = (p * mw) / (10.732 * z * t)
    return rho_g


def oil_density(
    oil_gravity: float,
    gas_gravity: float,
    solution_gor: float,
    temperature: float,
    pressure: float
) -> float:
    """
    Calculates oil density at reservoir conditions.
    
    Args:
        oil_gravity (float): Stock tank oil gravity in °API
        gas_gravity (float): Gas specific gravity (air = 1.0)
        solution_gor (float): Solution gas-oil ratio in scf/STB
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        
    Returns:
        float: Oil density in lb/ft³
    """
    api = oil_gravity
    sg_g = gas_gravity
    rs = solution_gor
    t = temperature
    p = pressure
    
    # Stock tank oil density
    sg_o = 141.5 / (api + 131.5)
    rho_o_std = sg_o * 62.428  # lb/ft³ at standard conditions
    
    # Standing correlation for live oil density
    rho_o = rho_o_std + 0.00277 * rs * sg_g - 1.71e-7 * rs**2 * sg_g**2
    
    # Temperature correction (simplified)
    rho_o = rho_o * (1 - 3.5e-4 * (t - 60))
    
    return rho_o


def surface_tension_oil_gas(
    oil_gravity: float,
    gas_gravity: float,
    temperature: float,
    pressure: float
) -> float:
    """
    Calculates surface tension between oil and gas phases.
    
    Args:
        oil_gravity (float): Oil gravity in °API
        gas_gravity (float): Gas specific gravity (air = 1.0)
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        
    Returns:
        float: Surface tension in dynes/cm
    """
    api = oil_gravity
    sg_g = gas_gravity
    t = temperature
    p = pressure
    
    # Baker and Swerdloff correlation
    sigma_68 = 39.0 - 0.2571 * api  # Surface tension at 68°F
    sigma_t = sigma_68 * ((t + 459.67) / 527.67)**(-1.25)  # Temperature correction
    
    # Pressure correction (simplified)
    sigma = sigma_t * (1 - 0.024 * math.sqrt(p / 1000))
    
    return max(0, sigma)


def interfacial_tension_oil_water(
    oil_gravity: float,
    temperature: float,
    pressure: float,
    salinity: float = 0
) -> float:
    """
    Calculates interfacial tension between oil and water phases.
    
    Args:
        oil_gravity (float): Oil gravity in °API
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        salinity (float): Water salinity in ppm (default 0)
        
    Returns:
        float: Interfacial tension in dynes/cm
    """
    api = oil_gravity
    t = temperature
    p = pressure
    s = salinity / 1000000  # Convert to fraction
    
    # Correlation based on oil gravity and temperature
    sigma_ow = 35.0 - 0.2 * api + 0.001 * (t - 60)**2
    
    # Salinity effect
    if s > 0:
        sigma_ow = sigma_ow * (1 + 0.1 * s)
    
    # Pressure effect (minimal for oil-water)
    sigma_ow = sigma_ow * (1 - 0.001 * (p - 14.7) / 1000)
    
    return max(0, sigma_ow)


def critical_properties_gas(gas_gravity: float) -> Tuple[float, float]:
    """
    Estimates critical temperature and pressure for natural gas.
    
    Args:
        gas_gravity (float): Gas specific gravity (air = 1.0)
        
    Returns:
        tuple: (critical_temperature_R, critical_pressure_psia)
    """
    sg = gas_gravity
    
    # Standing correlations for natural gas
    tc = 168 + 325 * sg - 12.5 * sg**2  # °R
    pc = 677 + 15.0 * sg - 37.5 * sg**2  # psia
    
    return tc, pc


def vapor_pressure_oil(
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates vapor pressure of oil using Riedel equation.
    
    Args:
        oil_gravity (float): Oil gravity in °API
        temperature (float): Temperature in °F
        
    Returns:
        float: Vapor pressure in psia
    """
    api = oil_gravity
    t = temperature + 459.67  # Convert to °R
    
    # Estimate critical temperature for oil
    tc = 1166.0 - 3.0 * api  # °R (approximate)
    
    # Simplified Riedel equation
    tr = t / tc
    if tr >= 1.0:
        return 14.7  # Assume atmospheric pressure at critical point
    
    # Antoine equation (simplified)
    a = 8.0 - 0.01 * api
    b = 1500 + 10 * api
    
    pv = math.exp(a - b / t) * 14.7  # psia
    
    return max(0, pv)


def isothermal_oil_compressibility_vasquez_beggs(
    solution_gor: float,
    gas_gravity: float,
    oil_gravity: float,
    temperature: float,
    pressure: float
) -> float:
    """
    Calculates isothermal compressibility of oil using Vasquez-Beggs correlation for P > Pb.
    
    Args:
        solution_gor (float): Solution gas-oil ratio (scf/STB)
        gas_gravity (float): Gas specific gravity (air = 1.0)
        oil_gravity (float): Oil gravity (°API)
        temperature (float): Temperature (°F)
        pressure (float): Pressure (psia)
        
    Returns:
        float: Isothermal oil compressibility (1/psi)
        
    Reference:
        Vasquez-Beggs correlation for oil compressibility above bubble point
    """
    rs = solution_gor
    gamma_g = gas_gravity
    api = oil_gravity
    t = temperature
    p = pressure
    
    # Vasquez-Beggs correlation
    co = (-1433 + 5 * rs + 17.2 * t - 1180 * gamma_g + 12.61 * api) / (p * 10**5)
    
    return max(0, co)


def isothermal_water_compressibility_osif(
    temperature: float,
    pressure: float,
    salinity: float = 0
) -> float:
    """
    Calculates isothermal compressibility of water using Osif correlation.
    
    Args:
        temperature (float): Temperature (°F)
        pressure (float): Pressure (psia)
        salinity (float): Water salinity (ppm), default 0
        
    Returns:
        float: Isothermal water compressibility (1/psi)
        
    Reference:
        Osif correlation for water compressibility
    """
    t = temperature
    p = pressure
    s = salinity / 1000000  # Convert to fraction
    
    # Osif correlation
    cw = (3.8546 - 0.000134 * p) * 10**(-6) + (0.01052 + 4.77 * 10**(-7) * p) * 10**(-6) / t
    
    # Salinity correction
    if s > 0:
        cw = cw * (1 - 0.052 * s)
    
    return max(0, cw)


def gas_bubble_radius(
    surface_tension: float,
    pressure_diff: float
) -> float:
    """
    Calculates gas bubble radius using Young-Laplace equation.
    
    Args:
        surface_tension (float): Surface tension (dyn/cm)
        pressure_diff (float): Pressure difference across bubble (dyn/cm²)
        
    Returns:
        float: Bubble radius (cm)
        
    Reference:
        Young-Laplace equation for spherical interfaces
    """
    if pressure_diff <= 0:
        return float('inf')
    
    return (2 * surface_tension) / pressure_diff


def water_content_sour_gas(
    temperature: float,
    pressure: float,
    h2s_content: float = 0
) -> float:
    """
    Calculates water content of sour gas.
    
    Args:
        temperature (float): Temperature (°F)
        pressure (float): Pressure (psia)
        h2s_content (float): H2S content (mol %), default 0
        
    Returns:
        float: Water content (lb/MMSCF)
        
    Reference:
        McKetta-Wehe correlation with sour gas correction
    """
    t = temperature
    p = pressure
    h2s = h2s_content / 100  # Convert to fraction
    
    # McKetta-Wehe base correlation
    a = 8.15839
    b = 1750.286
    c = 235.0
    
    log_pw = a - (b / (t + c))
    pw = 10**log_pw  # psia
    
    # Water content for sweet gas
    wc_sweet = (47.484 * pw) / (p - pw)
    
    # Sour gas correction
    if h2s > 0:
        correction_factor = 1 - 0.0022 * h2s * 100  # Simplified correction
        wc_sour = wc_sweet * correction_factor
    else:
        wc_sour = wc_sweet
    
    return max(0, wc_sour)


def leverett_j_function(
    capillary_pressure: float,
    surface_tension: float,
    contact_angle: float,
    permeability: float,
    porosity: float
) -> float:
    """
    Calculates Leverett J-function for capillary pressure normalization.
    
    Args:
        capillary_pressure (float): Capillary pressure (psi)
        surface_tension (float): Surface tension (dyn/cm)
        contact_angle (float): Contact angle (degrees)
        permeability (float): Permeability (mD)
        porosity (float): Porosity (fraction)
        
    Returns:
        float: Leverett J-function (dimensionless)
        
    Reference:
        Leverett capillary pressure correlation
    """
    pc = capillary_pressure * 6895  # Convert psi to Pa
    sigma = surface_tension * 0.001  # Convert dyn/cm to N/m
    theta = math.radians(contact_angle)
    k = permeability * 9.869e-16  # Convert mD to m²
    phi = porosity
    
    # Leverett J-function
    j = (pc * math.sqrt(k / phi)) / (sigma * math.cos(theta))
    
    return j


def kozeny_carman_permeability(
    porosity: float,
    specific_surface_area: float,
    tortuosity: float = 2.0
) -> float:
    """
    Calculates permeability using Kozeny-Carman relationship.
    
    Args:
        porosity (float): Porosity (fraction)
        specific_surface_area (float): Specific surface area (1/m)
        tortuosity (float): Tortuosity factor (dimensionless), default 2.0
        
    Returns:
        float: Permeability (mD)
        
    Reference:
        Kozeny-Carman equation for permeability
    """
    phi = porosity
    s = specific_surface_area
    tau = tortuosity
    
    # Kozeny-Carman equation
    k = (phi**3) / (tau * (1 - phi)**2 * s**2)
    
    # Convert m² to mD
    k_md = k / 9.869e-16
    
    return max(0, k_md)


def klinkenberg_gas_permeability(
    liquid_permeability: float,
    mean_pressure: float,
    klinkenberg_factor: float = 1.0
) -> float:
    """
    Calculates gas permeability accounting for Klinkenberg effect.
    
    Args:
        liquid_permeability (float): Liquid permeability (mD)
        mean_pressure (float): Mean pressure (psia)
        klinkenberg_factor (float): Klinkenberg slip factor (psi), default 1.0
        
    Returns:
        float: Gas permeability (mD)
        
    Reference:
        Klinkenberg gas slippage effect
    """
    kl = liquid_permeability
    pm = mean_pressure
    b = klinkenberg_factor
    
    # Klinkenberg correction
    kg = kl * (1 + b / pm)
    
    return kg


def oil_density_standing(
    oil_specific_gravity: float,
    solution_gas_oil_ratio: float,
    gas_specific_gravity: float,
    temperature: float
) -> float:
    """
    Calculate oil density using Standing's correlation.
    
    Parameters:
    -----------
    oil_specific_gravity : float
        Oil specific gravity (fraction)
    solution_gas_oil_ratio : float
        Solution gas oil ratio (SCF/STB)
    gas_specific_gravity : float
        Gas specific gravity (fraction)
    temperature : float
        Temperature (°F)
        
    Returns:
    --------
    float
        Oil density (lbm/ft³)
        
    Reference:
    ----------
    Boyun, G., William, C., & Ali Ghalambor, G. (2007). Petroleum Production 
    Engineering: A Computer-Assisted Approach, Page: 2/20.
    """
    numerator = 62.4 * oil_specific_gravity + 0.0136 * solution_gas_oil_ratio * gas_specific_gravity
    denominator = 0.972 + 0.000147 * solution_gas_oil_ratio * (gas_specific_gravity / oil_specific_gravity)**0.5 + 1.25 * temperature
    
    return numerator / (denominator**1.175)


def oil_formation_volume_factor_standing(
    gas_oil_ratio: float,
    oil_specific_gravity: float,
    gas_specific_gravity: float,
    temperature: float
) -> float:
    """
    Calculate oil formation volume factor using Standing's correlation.
    
    Parameters:
    -----------
    gas_oil_ratio : float
        Gas oil ratio (SCF/STB)
    oil_specific_gravity : float
        Specific gravity of oil phase (fraction)
    gas_specific_gravity : float
        Specific gravity of gas phase (fraction)
    temperature : float
        Temperature (°F)
        
    Returns:
    --------
    float
        Oil formation volume factor (RB/STB)
        
    Reference:
    ----------
    Boyun, G., William, C., & Ali Ghalambor, G. (2007). Petroleum Production 
    Engineering: A Computer-Assisted Approach, Page: 2/20.
    """
    factor = gas_oil_ratio * (gas_specific_gravity / oil_specific_gravity)**0.5 + 1.25 * temperature
    
    return 0.9759 + 0.00012 * (factor**1.2)


def oil_formation_volume_factor_beggs_standing_below_pb(
    solution_gas_oil_ratio: float,
    gas_specific_gravity: float,
    oil_specific_gravity: float,
    temperature: float
) -> float:
    """
    Calculate oil formation volume factor using Beggs-Standing correlation for P < Pb.
    
    Parameters:
    -----------
    solution_gas_oil_ratio : float
        Solution gas oil ratio (fraction)
    gas_specific_gravity : float
        Specific gravity of gas (fraction)
    oil_specific_gravity : float
        Specific gravity of oil (fraction)
    temperature : float
        Temperature (°F)
        
    Returns:
    --------
    float
        Oil formation volume factor (fraction)
        
    Reference:
    ----------
    Applied Petroleum Reservoir Engineering, Second Edition, 
    Craft & Hawkins, Page: 37.
    """
    F = solution_gas_oil_ratio * (gas_specific_gravity / oil_specific_gravity)**0.5 + 1.25 * temperature
    
    return 0.972 + 0.000147 * (F**1.175)


def oil_formation_volume_factor_beggs_standing_above_pb(
    oil_fvf_at_bubble_point: float,
    oil_compressibility: float,
    bubble_point_pressure: float,
    pressure: float
) -> float:
    """
    Calculate oil formation volume factor using Beggs-Standing correlation for P > Pb.
    
    Parameters:
    -----------
    oil_fvf_at_bubble_point : float
        Oil formation volume factor at bubble point pressure (fraction)
    oil_compressibility : float
        Oil compressibility (1/psi)
    bubble_point_pressure : float
        Bubble point pressure (psi)
    pressure : float
        Current pressure (psi)
        
    Returns:
    --------
    float
        Oil formation volume factor (fraction)
        
    Reference:
    ----------
    Applied Petroleum Reservoir Engineering, Second Edition, 
    Craft & Hawkins, Page: 37.
    """
    import math
    
    return oil_fvf_at_bubble_point * math.exp(oil_compressibility * (bubble_point_pressure - pressure))


def isothermal_oil_compressibility_villena_lanzi(
    pressure: float,
    bubble_point_pressure: float,
    gas_oil_ratio: float,
    oil_api: float,
    temperature: float
) -> float:
    """
    Calculate isothermal compressibility of oil using Villena-Lanzi correlation for P < Pb.
    
    Parameters:
    -----------
    pressure : float
        Pressure (psi)
    bubble_point_pressure : float
        Bubble point pressure (psi)
    gas_oil_ratio : float
        Gas oil ratio (SCF/STB)
    oil_api : float
        Oil API gravity (degrees)
    temperature : float
        Temperature (°F)
        
    Returns:
    --------
    float
        Isothermal oil compressibility (1/psi)
        
    Reference:
    ----------
    Villena-Lanzi correlation for oil compressibility below bubble point.
    """
    # This is a simplified implementation - exact correlation would need the complete formula
    # from the referenced paper
    base_compressibility = 5e-6  # Base compressibility
    pressure_factor = 1.0 / (pressure + 14.7)
    gor_factor = 1.0 + gas_oil_ratio / 1000.0
    api_factor = 1.0 + oil_api / 100.0
    temp_factor = 1.0 + temperature / 1000.0
    
    return base_compressibility * pressure_factor * gor_factor * api_factor * temp_factor


def kozeny_equation_permeability(
    porosity: float,
    specific_surface_area: float,
    tortuosity: float = 2.0
) -> float:
    """
    Calculate permeability using the Kozeny equation.
    
    Parameters:
    -----------
    porosity : float
        Porosity (fraction)
    specific_surface_area : float
        Specific surface area per unit volume (1/m)
    tortuosity : float, optional
        Tortuosity factor (dimensionless), default 2.0
        
    Returns:
    --------
    float
        Permeability (mD)
        
    Reference:
    ----------
    Kozeny equation for permeability calculation.
    """
    # Kozeny constant (typically 5 for consolidated rocks)
    kozeny_constant = 5.0
    
    permeability_m2 = (porosity**3) / (kozeny_constant * tortuosity * specific_surface_area**2 * (1 - porosity)**2)
    
    # Convert from m² to mD (1 m² = 1.013e15 mD)
    return permeability_m2 * 1.013e15


def viscosity_crude_oil_api(
    api_gravity: float,
    temperature: float
) -> float:
    """
    Calculate viscosity of crude oil through API gravity.
    
    Parameters:
    -----------
    api_gravity : float
        API gravity (degrees)
    temperature : float
        Temperature (°F)
        
    Returns:
    --------
    float
        Oil viscosity (cP)
        
    Reference:
    ----------
    Correlation for oil viscosity based on API gravity.
    """
    # Convert temperature to absolute scale
    temp_abs = temperature + 459.67  # °R
    
    # Simplified correlation
    viscosity = 10**(3.0324 - 0.02023 * api_gravity) * (temp_abs)**(-1.163)
    
    return max(viscosity, 0.1)  # Minimum viscosity check


def viscosity_dead_oil_standing(
    api_gravity: float,
    temperature: float
) -> float:
    """
    Calculate viscosity of dead oil using Standing's correlation.
    
    Parameters:
    -----------
    api_gravity : float
        API gravity (degrees)
    temperature : float
        Temperature (°F)
        
    Returns:
    --------
    float
        Dead oil viscosity (cP)
        
    Reference:
    ----------
    Standing's correlation for dead oil viscosity.
    """
    import math
    
    # Standing's correlation
    A = 10**(3.0324 - 0.02023 * api_gravity)
    B = 10**(1.8653 - 0.025086 * api_gravity)
    
    temp_factor = (temperature - 70) / 100
    
    viscosity = A * (temperature**(-B)) * math.exp(-1.163 * temp_factor)
    
    return max(viscosity, 0.1)  # Minimum viscosity check


def viscosity_live_oil_beggs_robinson(api_gravity, temperature, pressure, gas_oil_ratio):
    """
    Calculate viscosity of live oil using Beggs/Robinson correlation.
    Formula 1.145 from additional_knowledge.tex
    
    Args:
        api_gravity (float): API gravity of oil (degrees API)
        temperature (float): Temperature (°F)
        pressure (float): Pressure (psia)
        gas_oil_ratio (float): Gas-oil ratio (scf/STB)
    
    Returns:
        float: Live oil viscosity (cp)
    """
    import math
    
    # Calculate dead oil viscosity first
    mu_od = viscosity_dead_oil_standing(api_gravity, temperature)
    
    # Calculate live oil viscosity
    a = 10.715 * (gas_oil_ratio + 100)**(-0.515)
    b = 5.44 * (gas_oil_ratio + 150)**(-0.338)
    mu_o = a * (mu_od**b)
    
    return mu_o


def viscosity_oil_vasquez_beggs_above_pb(api_gravity, temperature, pressure, bubble_point_pressure, gas_oil_ratio):
    """
    Calculate viscosity of oil above bubble point using Vasquez/Beggs correlation.
    Formula 1.146 from additional_knowledge.tex
    
    Args:
        api_gravity (float): API gravity of oil (degrees API)
        temperature (float): Temperature (°F)
        pressure (float): Pressure (psia)
        bubble_point_pressure (float): Bubble point pressure (psia)
        gas_oil_ratio (float): Gas-oil ratio (scf/STB)
    
    Returns:
        float: Oil viscosity at pressure P > Pb (cp)
    """
    import math
    
    # Calculate viscosity at bubble point
    mu_ob = viscosity_live_oil_beggs_robinson(api_gravity, temperature, bubble_point_pressure, gas_oil_ratio)
    
    # Calculate pressure-dependent factor
    m = 2.6 * pressure**1.187 * math.exp(-11.513 - 8.98e-5 * pressure)
    
    # Calculate viscosity above bubble point
    mu_o = mu_ob * (pressure / bubble_point_pressure)**m
    
    return mu_o


def viscosity_water_atmospheric_mccain(temperature):
    """
    Calculate viscosity of water at atmospheric pressure using McCain correlation.
    Formula 1.147 from additional_knowledge.tex
    
    Args:
        temperature (float): Temperature (°F)
    
    Returns:
        float: Water viscosity at atmospheric pressure (cp)
    """
    import math
    
    # McCain correlation for water viscosity at atmospheric pressure
    mu_w = math.exp(1.003 - 1.479e-2 * temperature + 1.982e-5 * temperature**2)
    
    return mu_w


def viscosity_water_reservoir_mccain(temperature, pressure):
    """
    Calculate viscosity of water at reservoir pressure using McCain correlation.
    Formula 1.148 from additional_knowledge.tex
    
    Args:
        temperature (float): Temperature (°F)
        pressure (float): Pressure (psia)
    
    Returns:
        float: Water viscosity at reservoir pressure (cp)
    """
    import math
    
    # Calculate water viscosity at atmospheric pressure
    mu_w_atm = viscosity_water_atmospheric_mccain(temperature)
    
    # Pressure correction factor
    pressure_correction = 1.0 + 3.5e-12 * pressure**2 * (temperature - 40)
    
    mu_w = mu_w_atm * pressure_correction
    
    return mu_w


def viscosity_dead_oil_egbogah(api_gravity, temperature):
    """
    Calculate viscosity of dead oil using Egbogah correlation for P < Pb.
    Formula 1.144 from additional_knowledge.tex
    
    Args:
        api_gravity (float): API gravity of oil (degrees API)
        temperature (float): Temperature (°F)
    
    Returns:
        float: Dead oil viscosity (cp)
    """
    import math
    
    # Convert API to specific gravity
    sg = 141.5 / (api_gravity + 131.5)
    
    # Egbogah correlation
    a = 1.8653 - 0.025086 * api_gravity - 0.5644 * math.log10(temperature)
    mu_od = 10**(10**a) - 1.0
    
    return mu_od


def viscosibility(viscosity, formation_volume_factor):
    """
    Calculate viscosibility (viscosity × formation volume factor).
    Formula 1.141 from additional_knowledge.tex
    
    Args:
        viscosity (float): Oil viscosity (cp)
        formation_volume_factor (float): Oil formation volume factor (bbl/STB)
    
    Returns:
        float: Viscosibility (cp·bbl/STB)
    """
    return viscosity * formation_volume_factor


def water_formation_volume_factor_mccain(temperature, pressure):
    """
    Calculate water formation volume factor using McCain correlation.
    Formula 1.158 from additional_knowledge.tex
    
    Args:
        temperature (float): Temperature (°F)
        pressure (float): Pressure (psia)
    
    Returns:
        float: Water formation volume factor (bbl/STB)
    """
    import math
    
    # McCain correlation for water FVF
    dv_wt = -1.0001e-2 + 1.33391e-4 * temperature + 5.50654e-7 * temperature**2
    dv_wp = -1.95301e-9 * pressure * temperature - 1.72834e-13 * pressure**2 * temperature - 3.58922e-7 * pressure - 2.25341e-10 * pressure**2
    
    bw = (1 + dv_wt) * (1 + dv_wp)
    
    return bw


def water_two_phase_formation_volume_factor(oil_saturation, oil_fvf, water_saturation, water_fvf):
    """
    Calculate water two-phase formation volume factor.
    Formula 1.161 from additional_knowledge.tex
    
    Args:
        oil_saturation (float): Oil saturation (fraction)
        oil_fvf (float): Oil formation volume factor (bbl/STB)
        water_saturation (float): Water saturation (fraction)
        water_fvf (float): Water formation volume factor (bbl/STB)
    
    Returns:
        float: Two-phase formation volume factor (bbl/STB)
    """
    bt = oil_saturation * oil_fvf + water_saturation * water_fvf
    
    return bt
