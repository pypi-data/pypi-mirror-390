"""
Rock properties calculations.

This module contains functions for calculating rock and formation properties including:
- Porosity and permeability relationships
- Rock compressibility
- Relative permeability
- Capillary pressure
- Formation evaluation
"""

import math
from typing import Union, Tuple, Optional


def porosity_from_logs(
    neutron_porosity: float,
    density_porosity: float,
    shale_volume: float = 0.0
) -> float:
    """
    Calculates effective porosity from neutron and density logs.
    
    Args:
        neutron_porosity (float): Neutron porosity in fraction
        density_porosity (float): Density porosity in fraction
        shale_volume (float): Shale volume fraction (default 0.0)
        
    Returns:
        float: Effective porosity in fraction
    """
    phi_n = neutron_porosity
    phi_d = density_porosity
    vsh = shale_volume
    
    # Average porosity with shale correction
    phi_avg = (phi_n + phi_d) / 2
    phi_eff = phi_avg - vsh * phi_avg  # Simplified shale correction
    
    return max(0, phi_eff)


def porosity_from_density_log(
    bulk_density: float,
    matrix_density: float,
    fluid_density: float
) -> float:
    """
    Calculates porosity from density log using standard formula.
    
    Args:
        bulk_density (float): Bulk density from log in g/cm³
        matrix_density (float): Matrix density in g/cm³ (2.65 for quartz)
        fluid_density (float): Fluid density in g/cm³ (1.0 for water)
        
    Returns:
        float: Porosity in fraction
    """
    rho_b = bulk_density
    rho_ma = matrix_density
    rho_f = fluid_density
    
    phi = (rho_ma - rho_b) / (rho_ma - rho_f)
    return max(0, min(1, phi))


def water_saturation_archie(
    formation_resistivity: float,
    water_resistivity: float,
    porosity: float,
    cementation_factor: float = 2.0,
    saturation_exponent: float = 2.0,
    tortuosity_factor: float = 1.0
) -> float:
    """
    Calculates water saturation using Archie's equation.
    
    Args:
        formation_resistivity (float): Formation resistivity in ohm-m
        water_resistivity (float): Formation water resistivity in ohm-m
        porosity (float): Porosity in fraction
        cementation_factor (float): Cementation exponent (m), default 2.0
        saturation_exponent (float): Saturation exponent (n), default 2.0
        tortuosity_factor (float): Tortuosity factor (a), default 1.0
        
    Returns:
        float: Water saturation in fraction
    """
    rt = formation_resistivity
    rw = water_resistivity
    phi = porosity
    m = cementation_factor
    n = saturation_exponent
    a = tortuosity_factor
    
    if phi <= 0:
        raise ValueError("Porosity must be positive")
    
    # Archie's equation
    sw = ((a * rw) / (rt * phi**m))**(1/n)
    return max(0, min(1, sw))


def permeability_from_porosity_kozeny_carman(
    porosity: float,
    grain_diameter: float,
    shape_factor: float = 180
) -> float:
    """
    Calculates permeability using Kozeny-Carman equation.
    
    Args:
        porosity (float): Porosity in fraction
        grain_diameter (float): Average grain diameter in mm
        shape_factor (float): Shape factor (default 180 for spherical grains)
        
    Returns:
        float: Permeability in md
    """
    phi = porosity
    d = grain_diameter
    k0 = shape_factor
    
    if phi <= 0 or phi >= 1:
        raise ValueError("Porosity must be between 0 and 1")
    
    # Kozeny-Carman equation
    k = (phi**3 * d**2) / (k0 * (1 - phi)**2)
    
    # Convert from mm² to md (1 md = 9.869e-16 m² = 9.869e-10 mm²)
    k_md = k / 9.869e-10
    
    return k_md


def permeability_timur_correlation(porosity: float, irreducible_water_saturation: float) -> float:
    """
    Calculates permeability using Timur correlation.
    
    Args:
        porosity (float): Porosity in fraction
        irreducible_water_saturation (float): Irreducible water saturation in fraction
        
    Returns:
        float: Permeability in md
    """
    phi = porosity
    swir = irreducible_water_saturation
    
    if phi <= 0 or swir <= 0:
        raise ValueError("Porosity and water saturation must be positive")
    
    # Timur correlation
    k = 0.136 * (phi**4.4) / (swir**2)
    
    return k


def rock_compressibility(
    porosity: float,
    pressure: float,
    compressibility_coefficient: float = 3e-6
) -> float:
    """
    Calculates rock compressibility.
    
    Args:
        porosity (float): Porosity in fraction
        pressure (float): Pressure in psia
        compressibility_coefficient (float): Rock compressibility coefficient in 1/psi
        
    Returns:
        float: Rock compressibility in 1/psi
    """
    phi = porosity
    p = pressure
    cr0 = compressibility_coefficient
    
    # Newman correlation
    cr = cr0 * (1 - 0.4 * phi) / (1 + 0.1 * p / 1000)
    
    return cr


def relative_permeability_oil_corey(
    water_saturation: float,
    irreducible_water_saturation: float,
    residual_oil_saturation: float,
    oil_endpoint: float = 1.0,
    oil_exponent: float = 2.0
) -> float:
    """
    Calculates oil relative permeability using Corey correlation.
    
    Args:
        water_saturation (float): Water saturation in fraction
        irreducible_water_saturation (float): Irreducible water saturation in fraction
        residual_oil_saturation (float): Residual oil saturation in fraction
        oil_endpoint (float): Oil relative permeability at irreducible water saturation
        oil_exponent (float): Corey exponent for oil
        
    Returns:
        float: Oil relative permeability (dimensionless)
    """
    sw = water_saturation
    swir = irreducible_water_saturation
    sor = residual_oil_saturation
    kro_max = oil_endpoint
    no = oil_exponent
    
    if sw < swir:
        return kro_max
    elif sw > (1 - sor):
        return 0
    else:
        # Normalized saturation
        so_n = (1 - sw - sor) / (1 - swir - sor)
        kro = kro_max * so_n**no
        return kro


def relative_permeability_water_corey(
    water_saturation: float,
    irreducible_water_saturation: float,
    residual_oil_saturation: float,
    water_endpoint: float = 1.0,
    water_exponent: float = 2.0
) -> float:
    """
    Calculates water relative permeability using Corey correlation.
    
    Args:
        water_saturation (float): Water saturation in fraction
        irreducible_water_saturation (float): Irreducible water saturation in fraction
        residual_oil_saturation (float): Residual oil saturation in fraction
        water_endpoint (float): Water relative permeability at residual oil saturation
        water_exponent (float): Corey exponent for water
        
    Returns:
        float: Water relative permeability (dimensionless)
    """
    sw = water_saturation
    swir = irreducible_water_saturation
    sor = residual_oil_saturation
    krw_max = water_endpoint
    nw = water_exponent
    
    if sw <= swir:
        return 0
    elif sw >= (1 - sor):
        return krw_max
    else:
        # Normalized saturation
        sw_n = (sw - swir) / (1 - swir - sor)
        krw = krw_max * sw_n**nw
        return krw


def capillary_pressure_brooks_corey(
    water_saturation: float,
    irreducible_water_saturation: float,
    entry_pressure: float,
    pore_size_distribution: float
) -> float:
    """
    Calculates capillary pressure using Brooks-Corey correlation.
    
    Args:
        water_saturation (float): Water saturation in fraction
        irreducible_water_saturation (float): Irreducible water saturation in fraction
        entry_pressure (float): Entry pressure in psi
        pore_size_distribution (float): Pore size distribution index (lambda)
        
    Returns:
        float: Capillary pressure in psi
    """
    sw = water_saturation
    swir = irreducible_water_saturation
    pe = entry_pressure
    lambda_param = pore_size_distribution
    
    if sw <= swir:
        return float('inf')  # Infinite capillary pressure
    else:
        # Effective saturation
        se = (sw - swir) / (1 - swir)
        pc = pe * se**(-1/lambda_param)
        return pc


def formation_factor(
    porosity: float,
    cementation_factor: float = 2.0,
    tortuosity_factor: float = 1.0
) -> float:
    """
    Calculates formation resistivity factor.
    
    Args:
        porosity (float): Porosity in fraction
        cementation_factor (float): Cementation exponent (m), default 2.0
        tortuosity_factor (float): Tortuosity factor (a), default 1.0
        
    Returns:
        float: Formation factor (dimensionless)
    """
    phi = porosity
    m = cementation_factor
    a = tortuosity_factor
    
    if phi <= 0:
        raise ValueError("Porosity must be positive")
    
    f = a / phi**m
    return f


def net_to_gross_ratio(
    net_thickness: float,
    gross_thickness: float
) -> float:
    """
    Calculates net-to-gross ratio.
    
    Args:
        net_thickness (float): Net pay thickness in ft
        gross_thickness (float): Gross thickness in ft
        
    Returns:
        float: Net-to-gross ratio (fraction)
    """
    if gross_thickness <= 0:
        raise ValueError("Gross thickness must be positive")
    
    ntg = net_thickness / gross_thickness
    return max(0, min(1, ntg))


def bulk_volume_oil(
    gross_rock_volume: float,
    net_to_gross: float,
    porosity: float,
    oil_saturation: float
) -> float:
    """
    Calculates bulk volume of oil in reservoir.
    
    Args:
        gross_rock_volume (float): Gross rock volume in acre-ft
        net_to_gross (float): Net-to-gross ratio in fraction
        porosity (float): Porosity in fraction
        oil_saturation (float): Oil saturation in fraction
        
    Returns:
        float: Bulk volume oil in acre-ft
    """
    grv = gross_rock_volume
    ntg = net_to_gross
    phi = porosity
    so = oil_saturation
    
    bvo = grv * ntg * phi * so
    return bvo


def hydrocarbon_pore_volume(
    bulk_volume: float,
    porosity: float,
    hydrocarbon_saturation: float
) -> float:
    """
    Calculates hydrocarbon pore volume.
    
    Args:
        bulk_volume (float): Bulk volume in acre-ft
        porosity (float): Porosity in fraction
        hydrocarbon_saturation (float): Hydrocarbon saturation in fraction
        
    Returns:
        float: Hydrocarbon pore volume in acre-ft
    """
    bv = bulk_volume
    phi = porosity
    sh = hydrocarbon_saturation
    
    hcpv = bv * phi * sh
    return hcpv


def porosity_ies_fdc_logs(
    interval_transit_time: float,
    matrix_transit_time: float,
    fluid_transit_time: float,
    bulk_density: float,
    matrix_density: float,
    fluid_density: float
) -> Tuple[float, float]:
    """
    Calculates porosity from IES (Interval Transit Time) and FDC (Formation Density) logs.
    
    Args:
        interval_transit_time (float): Interval transit time (μs/ft)
        matrix_transit_time (float): Matrix transit time (μs/ft)
        fluid_transit_time (float): Fluid transit time (μs/ft)
        bulk_density (float): Bulk density from log (g/cm³)
        matrix_density (float): Matrix density (g/cm³)
        fluid_density (float): Fluid density (g/cm³)
        
    Returns:
        Tuple[float, float]: (IES porosity, FDC porosity) in fractions
        
    Reference:
        Standard log analysis techniques
    """
    dt = interval_transit_time
    dt_ma = matrix_transit_time
    dt_f = fluid_transit_time
    rho_b = bulk_density
    rho_ma = matrix_density
    rho_f = fluid_density
    
    # IES (sonic) porosity
    if dt_f - dt_ma != 0:
        phi_ies = (dt - dt_ma) / (dt_f - dt_ma)
    else:
        phi_ies = 0
    
    # FDC (density) porosity
    if rho_ma - rho_f != 0:
        phi_fdc = (rho_ma - rho_b) / (rho_ma - rho_f)
    else:
        phi_fdc = 0
    
    # Ensure reasonable bounds
    phi_ies = max(0, min(1, phi_ies))
    phi_fdc = max(0, min(1, phi_fdc))
    
    return phi_ies, phi_fdc


def ineffective_porosity(
    total_porosity: float,
    irreducible_water_saturation: float,
    residual_oil_saturation: float = 0
) -> float:
    """
    Calculates ineffective porosity.
    
    Args:
        total_porosity (float): Total porosity (fraction)
        irreducible_water_saturation (float): Irreducible water saturation (fraction)
        residual_oil_saturation (float): Residual oil saturation (fraction), default 0
        
    Returns:
        float: Ineffective porosity (fraction)
        
    Reference:
        Standard reservoir characterization calculations
    """
    phi_t = total_porosity
    swir = irreducible_water_saturation
    sor = residual_oil_saturation
    
    # Ineffective porosity includes trapped fluids
    phi_ineff = phi_t * (swir + sor)
    
    return min(phi_t, max(0, phi_ineff))


def geertsma_porosity_transit_time(
    porosity: float,
    matrix_transit_time: float,
    fluid_transit_time: float,
    compaction_coefficient: float = 1.0
) -> float:
    """
    Calculates porosity-transit time relationship using Geertsma's model.
    
    Args:
        porosity (float): Porosity (fraction)
        matrix_transit_time (float): Matrix transit time (μs/ft)
        fluid_transit_time (float): Fluid transit time (μs/ft)
        compaction_coefficient (float): Compaction coefficient, default 1.0
        
    Returns:
        float: Calculated transit time (μs/ft)
        
    Reference:
        Geertsma's model for porosity/transit-time relationship
    """
    phi = porosity
    dt_ma = matrix_transit_time
    dt_f = fluid_transit_time
    c = compaction_coefficient
    
    # Geertsma's model
    dt = dt_ma + (dt_f - dt_ma) * phi * c
    
    return dt


def normalized_saturation(
    current_saturation: float,
    irreducible_saturation: float,
    maximum_saturation: float = 1.0
) -> float:
    """
    Calculates normalized saturation.
    
    Args:
        current_saturation (float): Current saturation (fraction)
        irreducible_saturation (float): Irreducible saturation (fraction)
        maximum_saturation (float): Maximum saturation (fraction), default 1.0
        
    Returns:
        float: Normalized saturation (fraction)
        
    Reference:
        Standard relative permeability calculations
    """
    s = current_saturation
    sir = irreducible_saturation
    smax = maximum_saturation
    
    if smax - sir <= 0:
        return 0
    
    # Normalized saturation
    sn = (s - sir) / (smax - sir)
    
    return max(0, min(1, sn))


def relative_permeability_corey(
    water_saturation: float,
    irreducible_water_saturation: float,
    residual_oil_saturation: float,
    corey_exponent_water: float = 2.0,
    corey_exponent_oil: float = 2.0,
    endpoint_krw: float = 1.0,
    endpoint_kro: float = 1.0
) -> Tuple[float, float]:
    """
    Calculates relative permeability using Corey exponents.
    
    Args:
        water_saturation (float): Water saturation (fraction)
        irreducible_water_saturation (float): Irreducible water saturation (fraction)
        residual_oil_saturation (float): Residual oil saturation (fraction)
        corey_exponent_water (float): Corey exponent for water, default 2.0
        corey_exponent_oil (float): Corey exponent for oil, default 2.0
        endpoint_krw (float): Endpoint relative permeability to water, default 1.0
        endpoint_kro (float): Endpoint relative permeability to oil, default 1.0
        
    Returns:
        Tuple[float, float]: (krw, kro) relative permeabilities
        
    Reference:
        Corey correlations for relative permeability
    """
    sw = water_saturation
    swir = irreducible_water_saturation
    sor = residual_oil_saturation
    nw = corey_exponent_water
    no = corey_exponent_oil
    krw_max = endpoint_krw
    kro_max = endpoint_kro
    
    # Normalized saturations
    sw_norm = (sw - swir) / (1 - swir - sor) if (1 - swir - sor) > 0 else 0
    so_norm = (1 - sw - sor) / (1 - swir - sor) if (1 - swir - sor) > 0 else 0
    
    # Ensure saturations are within bounds
    sw_norm = max(0, min(1, sw_norm))
    so_norm = max(0, min(1, so_norm))
    
    # Corey correlations
    krw = krw_max * (sw_norm**nw)
    kro = kro_max * (so_norm**no)
    
    return krw, kro


def waxman_smits_clean_sands(
    porosity: float,
    water_saturation: float,
    water_resistivity: float,
    formation_factor: float = None,
    saturation_exponent: float = 2.0
) -> float:
    """
    Calculates formation resistivity using Waxman-Smits model for clean sands.
    
    Args:
        porosity (float): Porosity (fraction)
        water_saturation (float): Water saturation (fraction)
        water_resistivity (float): Formation water resistivity (ohm-m)
        formation_factor (float): Formation factor, calculated if None
        saturation_exponent (float): Saturation exponent, default 2.0
        
    Returns:
        float: Formation resistivity (ohm-m)
        
    Reference:
        Waxman and Smits model for clean sands
    """
    phi = porosity
    sw = water_saturation
    rw = water_resistivity
    n = saturation_exponent
    
    # Calculate formation factor if not provided
    if formation_factor is None:
        # Archie's law for formation factor
        a = 1.0  # Tortuosity factor
        m = 2.0  # Cementation exponent
        f = a / (phi**m)
    else:
        f = formation_factor
    
    if sw <= 0:
        return float('inf')
    
    # Waxman-Smits equation for clean sands
    rt = (f * rw) / (sw**n)
    
    return rt


def interstitial_velocity(
    darcy_velocity: float,
    porosity: float,
    tortuosity: float = 1.0
) -> float:
    """
    Calculates interstitial (pore) velocity from Darcy velocity.
    
    Args:
        darcy_velocity (float): Darcy velocity (ft/day)
        porosity (float): Porosity (fraction)
        tortuosity (float): Tortuosity factor (dimensionless), default 1.0
        
    Returns:
        float: Interstitial velocity (ft/day)
        
    Reference:
        Basic porous media flow calculations
    """
    v_darcy = darcy_velocity
    phi = porosity
    tau = tortuosity
    
    if phi <= 0:
        return 0
    
    # Interstitial velocity
    v_int = (v_darcy * tau) / phi
    
    return v_int


def volumetric_heat_capacity_reservoir(
    rock_density: float,
    rock_heat_capacity: float,
    fluid_density: float,
    fluid_heat_capacity: float,
    porosity: float
) -> float:
    """
    Calculates volumetric heat capacity of a reservoir.
    
    Args:
        rock_density (float): Rock density (lb/ft³)
        rock_heat_capacity (float): Rock specific heat capacity (BTU/lb/°F)
        fluid_density (float): Fluid density (lb/ft³)
        fluid_heat_capacity (float): Fluid specific heat capacity (BTU/lb/°F)
        porosity (float): Porosity (fraction)
        
    Returns:
        float: Volumetric heat capacity (BTU/ft³/°F)
        
    Reference:
        Thermal properties of reservoir systems
    """
    rho_r = rock_density
    cp_r = rock_heat_capacity
    rho_f = fluid_density
    cp_f = fluid_heat_capacity
    phi = porosity
    
    # Volumetric heat capacity
    rho_cp = (1 - phi) * rho_r * cp_r + phi * rho_f * cp_f
    
    return rho_cp
