"""
Production engineering calculations.

This module contains functions for production engineering calculations including:
- Well performance and inflow performance
- Artificial lift calculations
- Nodal analysis
- Well testing analysis
- Flow through chokes and restrictions
"""

import math
from typing import Union, Tuple, Optional


def vogel_ipr(
    reservoir_pressure: float,
    bottomhole_pressure: float,
    maximum_oil_rate: float
) -> float:
    """
    Calculates oil production rate using Vogel's IPR correlation.
    
    Args:
        reservoir_pressure (float): Reservoir pressure in psia
        bottomhole_pressure (float): Bottomhole flowing pressure in psia
        maximum_oil_rate (float): Maximum oil rate at zero bottomhole pressure in STB/day
        
    Returns:
        float: Oil production rate in STB/day
    """
    pr = reservoir_pressure
    pwf = bottomhole_pressure
    qmax = maximum_oil_rate
    
    # Vogel's IPR equation
    q = qmax * (1 - 0.2 * (pwf / pr) - 0.8 * (pwf / pr)**2)
    return max(0, q)  # Ensure non-negative flow rate


def productivity_index(
    flow_rate: float,
    reservoir_pressure: float,
    bottomhole_pressure: float
) -> float:
    """
    Calculates productivity index for a well.
    
    Args:
        flow_rate (float): Production rate in STB/day
        reservoir_pressure (float): Reservoir pressure in psia
        bottomhole_pressure (float): Bottomhole flowing pressure in psia
        
    Returns:
        float: Productivity index in STB/day/psi
    """
    q = flow_rate
    pr = reservoir_pressure
    pwf = bottomhole_pressure
    
    if pr <= pwf:
        raise ValueError("Reservoir pressure must be greater than bottomhole pressure")
    
    pi = q / (pr - pwf)
    return pi


def darcy_radial_flow(
    permeability: float,
    thickness: float,
    pressure_drop: float,
    viscosity: float,
    formation_volume_factor: float,
    wellbore_radius: float,
    drainage_radius: float
) -> float:
    """
    Calculates flow rate using Darcy's equation for radial flow.
    
    Args:
        permeability (float): Formation permeability in md
        thickness (float): Net pay thickness in ft
        pressure_drop (float): Pressure drop in psi
        viscosity (float): Fluid viscosity in cp
        formation_volume_factor (float): Formation volume factor in res bbl/STB
        wellbore_radius (float): Wellbore radius in ft
        drainage_radius (float): Drainage radius in ft
        
    Returns:
        float: Flow rate in STB/day
    """
    k = permeability
    h = thickness
    dp = pressure_drop
    mu = viscosity
    bo = formation_volume_factor
    rw = wellbore_radius
    re = drainage_radius
    
    if re <= rw:
        raise ValueError("Drainage radius must be greater than wellbore radius")
    
    q = (0.00708 * k * h * dp) / (mu * bo * math.log(re / rw))
    return q


def skin_factor(
    actual_productivity_index: float,
    ideal_productivity_index: float
) -> float:
    """
    Calculates skin factor from productivity indices.
    
    Args:
        actual_productivity_index (float): Actual PI in STB/day/psi
        ideal_productivity_index (float): Ideal PI in STB/day/psi
        
    Returns:
        float: Skin factor (dimensionless)
    """
    pi_actual = actual_productivity_index
    pi_ideal = ideal_productivity_index
    
    if pi_actual <= 0 or pi_ideal <= 0:
        raise ValueError("Productivity indices must be positive")
    
    skin = (pi_ideal / pi_actual) - 1
    return skin


def gas_well_deliverability_rawlins_schellhardt(
    absolute_open_flow_potential: float,
    flowing_bottomhole_pressure: float,
    reservoir_pressure: float,
    flow_exponent: float = 0.5
) -> float:
    """
    Calculates gas well deliverability using Rawlins-Schellhardt equation.
    
    Args:
        absolute_open_flow_potential (float): AOF in Mscf/day
        flowing_bottomhole_pressure (float): Flowing BHP in psia
        reservoir_pressure (float): Reservoir pressure in psia
        flow_exponent (float): Flow exponent (n), typically 0.5-1.0
        
    Returns:
        float: Gas flow rate in Mscf/day
    """
    aof = absolute_open_flow_potential
    pwf = flowing_bottomhole_pressure
    pr = reservoir_pressure
    n = flow_exponent
    
    if pr <= pwf:
        raise ValueError("Reservoir pressure must be greater than flowing pressure")
    
    qg = aof * (1 - (pwf / pr)**2)**n
    return qg


def choke_flow_rate_gas(
    upstream_pressure: float,
    downstream_pressure: float,
    choke_diameter: float,
    gas_gravity: float,
    temperature: float,
    discharge_coefficient: float = 0.85
) -> float:
    """
    Calculates gas flow rate through a choke.
    
    Args:
        upstream_pressure (float): Upstream pressure in psia
        downstream_pressure (float): Downstream pressure in psia
        choke_diameter (float): Choke diameter in inches
        gas_gravity (float): Gas specific gravity (air = 1.0)
        temperature (float): Temperature in °R
        discharge_coefficient (float): Discharge coefficient
        
    Returns:
        float: Gas flow rate in Mscf/day
    """
    p1 = upstream_pressure
    p2 = downstream_pressure
    d = choke_diameter
    sg = gas_gravity
    t = temperature
    cd = discharge_coefficient
    
    # Critical pressure ratio
    critical_ratio = 0.55  # Approximate for natural gas
    
    if p2 / p1 < critical_ratio:
        # Critical flow
        qg = 0.0125 * cd * (d**2) * p1 / math.sqrt(sg * t)
    else:
        # Subcritical flow
        qg = 0.0125 * cd * (d**2) * p1 * math.sqrt((p1**2 - p2**2) / (sg * t * p1**2))
    
    return qg * 1000  # Convert to Mscf/day


def multiphase_flow_beggs_brill(
    liquid_rate: float,
    gas_rate: float,
    pipe_diameter: float,
    pipe_inclination: float,
    liquid_density: float,
    gas_density: float,
    liquid_viscosity: float,
    gas_viscosity: float
) -> Tuple[float, float]:
    """
    Calculates pressure gradient using Beggs-Brill correlation.
    
    Args:
        liquid_rate (float): Liquid flow rate in bbl/day
        gas_rate (float): Gas flow rate in Mscf/day
        pipe_diameter (float): Pipe diameter in inches
        pipe_inclination (float): Pipe inclination angle in degrees
        liquid_density (float): Liquid density in lb/ft³
        gas_density (float): Gas density in lb/ft³
        liquid_viscosity (float): Liquid viscosity in cp
        gas_viscosity (float): Gas viscosity in cp
        
    Returns:
        tuple: (pressure_gradient_psi_per_ft, liquid_holdup)
    """
    ql = liquid_rate / 86400  # Convert to ft³/sec
    qg = gas_rate * 1000 / 86400  # Convert to ft³/sec
    d = pipe_diameter / 12  # Convert to ft
    theta = math.radians(pipe_inclination)
    rho_l = liquid_density
    rho_g = gas_density
    mu_l = liquid_viscosity
    mu_g = gas_viscosity
    
    # Calculate superficial velocities
    area = math.pi * d**2 / 4
    vsl = ql / area  # Superficial liquid velocity
    vsg = qg / area  # Superficial gas velocity
    vm = vsl + vsg  # Mixture velocity
    
    # Calculate liquid holdup (simplified)
    lambda_l = vsl / vm if vm > 0 else 0
    
    # Simplified liquid holdup calculation
    if lambda_l < 0.01:
        hl = lambda_l
    else:
        hl = 0.845 * lambda_l**0.351  # Approximate correlation
    
    # Calculate mixture density
    rho_m = hl * rho_l + (1 - hl) * rho_g
    
    # Calculate pressure gradient components
    # Hydrostatic component
    dp_dz_h = rho_m * math.sin(theta) / 144  # psi/ft
    
    # Friction component (simplified)
    rho_ns = lambda_l * rho_l + (1 - lambda_l) * rho_g
    mu_ns = lambda_l * mu_l + (1 - lambda_l) * mu_g
    
    # Reynolds number
    re = rho_ns * vm * d / (mu_ns * 6.72e-4)
    
    # Friction factor (simplified)
    if re < 2100:
        f = 16 / re
    else:
        f = 0.0791 / re**0.25
    
    # Friction pressure gradient
    dp_dz_f = (2 * f * rho_ns * vm**2) / (32.174 * d * 144)
    
    # Total pressure gradient
    dp_dz_total = dp_dz_h + dp_dz_f
    
    return dp_dz_total, hl


def well_test_analysis_horner(
    pressure_data: list,
    time_data: list,
    production_time: float,
    flow_rate: float,
    porosity: float,
    viscosity: float,
    total_compressibility: float,
    formation_volume_factor: float,
    thickness: float
) -> Tuple[float, float]:
    """
    Analyzes well test data using Horner plot method.
    
    Args:
        pressure_data (list): List of pressure measurements in psia
        time_data (list): List of time measurements (shutin time) in hours
        production_time (float): Production time before shutin in hours
        flow_rate (float): Production rate before shutin in STB/day
        porosity (float): Porosity fraction
        viscosity (float): Oil viscosity in cp
        total_compressibility (float): Total compressibility in 1/psi
        formation_volume_factor (float): Formation volume factor in res bbl/STB
        thickness (float): Net pay thickness in ft
        
    Returns:
        tuple: (permeability_md, skin_factor)
    """
    # This is a simplified implementation
    # In practice, you would perform linear regression on Horner plot
    
    if len(pressure_data) != len(time_data):
        raise ValueError("Pressure and time data must have same length")
    
    # Calculate Horner time function
    tp = production_time
    horner_time = [(tp + dt) / dt for dt in time_data]
    
    # Find slope of pressure vs log(horner_time) - simplified
    if len(pressure_data) >= 2:
        p1, p2 = pressure_data[0], pressure_data[-1]
        t1, t2 = horner_time[0], horner_time[-1]
        
        if t2 > t1:
            slope = (p2 - p1) / math.log(t2 / t1)
        else:
            slope = 0
    else:
        slope = 0
    
    # Calculate permeability
    if slope != 0:
        k = (162.6 * flow_rate * viscosity * formation_volume_factor) / (abs(slope) * thickness)
    else:
        k = 0
    
    # Calculate skin (simplified)
    if len(pressure_data) > 0 and slope != 0:
        pi = pressure_data[-1]  # Initial pressure estimate
        p1hr = pressure_data[0] if len(pressure_data) > 0 else pi
        
        skin = 1.151 * ((p1hr - pressure_data[0]) / abs(slope) - 1.151 * math.log(k / (porosity * viscosity * total_compressibility * 0.0002637)) + 3.23)
    else:
        skin = 0
    
    return k, skin


def gas_well_productivity_index(
    flow_rate: float,
    reservoir_pressure: float,
    bottomhole_pressure: float
) -> float:
    """
    Calculates productivity index for a gas well.
    
    Args:
        flow_rate (float): Gas flow rate (MSCF/day)
        reservoir_pressure (float): Reservoir pressure (psia)
        bottomhole_pressure (float): Bottom hole flowing pressure (psia)
        
    Returns:
        float: Gas well productivity index (MSCF/day/psi²)
        
    Reference:
        Standard gas well performance calculations
    """
    q = flow_rate
    pr = reservoir_pressure
    pwf = bottomhole_pressure
    
    if pr**2 - pwf**2 == 0:
        return 0
    
    # Gas well PI using squared pressure difference
    pi = q / (pr**2 - pwf**2)
    
    return pi


def deliverability_equation_shallow_gas(
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
        thickness (float): Net pay thickness (ft)
        temperature (float): Temperature (°R)
        viscosity (float): Gas viscosity (cP)
        z_factor (float): Gas compressibility factor (dimensionless)
        drainage_radius (float): Drainage radius (ft)
        wellbore_radius (float): Wellbore radius (ft)
        
    Returns:
        float: Performance coefficient (dimensionless)
        
    Reference:
        Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
        Gulf Publishing of Elsevier, Chapter: 3, Page: 287.
    """
    import math
    
    return (permeability * thickness) / \
           (1422 * temperature * viscosity * z_factor * math.log(drainage_radius / wellbore_radius) - 0.5)


def dimensionless_pressure_kamal_brigham(
    permeability: float,
    thickness: float,
    pressure_difference: float,
    flow_rate: float,
    viscosity: float,
    formation_volume_factor: float
) -> float:
    """
    Calculate dimensionless pressure using Kamal and Brigham method.
    
    Parameters:
    -----------
    permeability : float
        Average permeability (mD)
    thickness : float
        Thickness (ft)
    pressure_difference : float
        Pressure difference (psi)
    flow_rate : float
        Flow rate (STB/day)
    viscosity : float
        Viscosity (cP)
    formation_volume_factor : float
        Formation volume factor (bbl/STB)
        
    Returns:
    --------
    float
        Dimensionless pressure (dimensionless)
        
    Reference:
    ----------
    Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
    Gulf Publishing of Elsevier, Chapter: 1, Page: 125.
    """
    return (permeability * thickness * pressure_difference) / \
           (141.2 * flow_rate * viscosity * formation_volume_factor)


def dimensionless_radius_radial_flow(
    radius: float,
    wellbore_radius: float
) -> float:
    """
    Calculate dimensionless radius for radial flow in constant-rate production.
    
    Parameters:
    -----------
    radius : float
        Effective radius or reservoir radius (ft)
    wellbore_radius : float
        Wellbore radius (ft)
        
    Returns:
    --------
    float
        Dimensionless radius (dimensionless)
        
    Reference:
    ----------
    Lee, J., Rollins, J. B., & Spivey, J. P. (2003). Pressure Transient Testing 
    (Vol. 9). Richardson, Texas: Society of Petroleum Engineers, Page: 8.
    """
    return radius / wellbore_radius


def dimensionless_time_myhill_stegemeier(
    steam_heat_capacity: float,
    reservoir_heat_capacity: float,
    overburden_heat_transfer_coeff: float,
    column_thickness: float,
    time: float
) -> float:
    """
    Calculate dimensionless time using Myhill and Stegemeier's method.
    
    Parameters:
    -----------
    steam_heat_capacity : float
        Volumetric heat capacity of steam (btu/ft³·K)
    reservoir_heat_capacity : float
        Volumetric heat capacity of the reservoir (btu/ft³·K)
    overburden_heat_transfer_coeff : float
        Overburden heat transfer coefficient (ft²/d)
    column_thickness : float
        Thickness of column (ft)
    time : float
        Time (day)
        
    Returns:
    --------
    float
        Dimensionless time (dimensionless)
        
    Reference:
    ----------
    Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
    New York, Chapter: 5, Page: 44.
    """
    return 4 * (steam_heat_capacity / reservoir_heat_capacity)**2 * \
           (overburden_heat_transfer_coeff / column_thickness**2) * time


def dimensionless_time_interference_testing(
    permeability: float,
    time: float,
    porosity: float,
    viscosity: float,
    total_compressibility: float,
    distance: float
) -> float:
    """
    Calculate dimensionless time for interference testing in homogeneous reservoirs.
    
    Parameters:
    -----------
    permeability : float
        Permeability (mD)
    time : float
        Time (hours)
    porosity : float
        Porosity (fraction)
    viscosity : float
        Viscosity (cP)
    total_compressibility : float
        Total compressibility (1/psi)
    distance : float
        Distance between wells (ft)
        
    Returns:
    --------
    float
        Dimensionless time (dimensionless)
        
    Reference:
    ----------
    Earlougher's method for interference testing.
    """
    # Convert time from hours to seconds for consistency
    time_seconds = time * 3600
    
    return (0.000264 * permeability * time_seconds) / \
           (porosity * viscosity * total_compressibility * distance**2)


def dimensionless_wellbore_storage_coefficient(
    wellbore_storage: float,
    porosity: float,
    total_compressibility: float,
    thickness: float,
    wellbore_radius: float
) -> float:
    """
    Calculate dimensionless wellbore storage coefficient for radial flow.
    
    Parameters:
    -----------
    wellbore_storage : float
        Wellbore storage coefficient (bbl/psi)
    porosity : float
        Porosity (fraction)
    total_compressibility : float
        Total compressibility (1/psi)
    thickness : float
        Formation thickness (ft)
    wellbore_radius : float
        Wellbore radius (ft)
        
    Returns:
    --------
    float
        Dimensionless wellbore storage coefficient (dimensionless)
        
    Reference:
    ----------
    Standard reservoir engineering formula for dimensionless wellbore storage.
    """
    import math
    
    return wellbore_storage / \
           (2 * math.pi * porosity * total_compressibility * thickness * wellbore_radius**2)


def vertical_well_critical_rate_craft_hawkins(
    penetration_ratio: float,
    drainage_radius: float,
    wellbore_radius: float,
    perforated_thickness: float,
    oil_column_thickness: float,
    oil_viscosity: float,
    oil_fvf: float,
    oil_permeability: float,
    static_pressure: float,
    flowing_pressure: float
) -> tuple:
    """
    Calculate critical rate for vertical wells using Craft and Hawkins method.
    
    Parameters:
    -----------
    penetration_ratio : float
        Penetration ratio (hp/h) (dimensionless)
    drainage_radius : float
        Radius of drainage (ft)
    wellbore_radius : float
        Radius of wellbore (ft)
    perforated_thickness : float
        Thickness of perforated interval (ft)
    oil_column_thickness : float
        Oil column thickness (ft)
    oil_viscosity : float
        Oil viscosity (cP)
    oil_fvf : float
        Oil formation volume factor (RB/STB)
    oil_permeability : float
        Effective oil permeability (mD)
    static_pressure : float
        Static well pressure (psi)
    flowing_pressure : float
        Flowing well pressure (psi)
        
    Returns:
    --------
    tuple
        (critical_rate (STB/day), productivity_ratio (dimensionless))
        
    Reference:
    ----------
    Joshi, S.D. 1991, Horizontal Well Technology. Tulsa, Oklahoma: 
    PennWell Publishing Company. Chapter: 8, Page: 254.
    """
    import math
    
    # Productivity ratio
    term1 = 1 + 7 * (wellbore_radius / (2 * penetration_ratio * oil_column_thickness))**0.5
    term2 = math.cos(penetration_ratio * 90 * math.pi / 180)  # Convert to radians
    PR = penetration_ratio * term1 * term2
    
    # Critical rate
    qo = (0.007078 * oil_permeability * oil_column_thickness * (static_pressure - flowing_pressure)) / \
         (oil_viscosity * oil_fvf * math.log(drainage_radius / wellbore_radius)) * PR
    
    return qo, PR


def vertical_well_critical_rate_hoyland_papatzacos(
    oil_column_thickness: float,
    perforated_interval: float,
    drainage_radius: float,
    oil_permeability: float,
    water_density: float,
    oil_viscosity: float,
    oil_density: float,
    oil_fvf: float
) -> float:
    """
    Calculate critical rate using Hoyland, Papatzacos, and Skjaeveland method for isotropic reservoirs.
    
    Parameters:
    -----------
    oil_column_thickness : float
        Oil column thickness (m)
    perforated_interval : float
        Perforated interval (m)
    drainage_radius : float
        Drainage radius (m)
    oil_permeability : float
        Effective oil permeability (mD)
    water_density : float
        Water density (kg/m³)
    oil_viscosity : float
        Oil viscosity (cP)
    oil_density : float
        Oil density (kg/m³)
    oil_fvf : float
        Oil formation volume factor (RB/STB)
        
    Returns:
    --------
    float
        Critical rate (m³/day)
        
    Reference:
    ----------
    Horizontal Well Technology, Joshi, Page: 257.
    """
    import math
    
    term1 = (water_density - oil_density) * oil_permeability
    term2 = oil_fvf * oil_viscosity * 10822
    term3 = (1 - (perforated_interval / oil_column_thickness)**2)**1.325
    term4 = oil_column_thickness**2.238
    term5 = (math.log(drainage_radius))**(-1.99)
    
    return (term1 / term2) * term3 * term4 * term5


def vertical_well_critical_rate_meyer_gardner_pirson_simultaneous(
    oil_density: float,
    water_density: float,
    drainage_radius: float,
    wellbore_radius: float,
    perforated_thickness: float,
    oil_column_thickness: float,
    oil_viscosity: float,
    oil_fvf: float,
    oil_permeability: float
) -> float:
    """
    Calculate critical rate using Meyer, Gardner, and Pirson method for simultaneous gas and water coning.
    
    Parameters:
    -----------
    oil_density : float
        Oil density (g/cc)
    water_density : float
        Water density (g/cc)
    drainage_radius : float
        Drainage radius (ft)
    wellbore_radius : float
        Radius of wellbore (ft)
    perforated_thickness : float
        Thickness of perforated interval (ft)
    oil_column_thickness : float
        Oil column thickness (ft)
    oil_viscosity : float
        Oil viscosity (cP)
    oil_fvf : float
        Oil formation volume factor (RB/STB)
    oil_permeability : float
        Effective oil permeability (mD)
        
    Returns:
    --------
    float
        Critical rate (STB/day)
        
    Reference:
    ----------
    Joshi, S.D. 1991, Horizontal Well Technology. Tulsa, Oklahoma: 
    PennWell Publishing Company. Chapter: 8, Page: 255.
    """
    import math
    
    term1 = 0.001535 * (water_density - oil_density) / math.log(drainage_radius / wellbore_radius)
    term2 = oil_permeability / (oil_viscosity * oil_fvf)
    term3 = oil_column_thickness**2 - perforated_thickness**2
    
    return term1 * term2 * term3


def vertical_well_critical_rate_meyer_gardner_pirson_water(
    oil_density: float,
    water_density: float,
    drainage_radius: float,
    wellbore_radius: float,
    perforated_thickness: float,
    oil_column_thickness: float,
    oil_viscosity: float,
    oil_fvf: float,
    oil_permeability: float
) -> float:
    """
    Calculate critical rate using Meyer, Gardner, and Pirson method for water coning only.
    
    Parameters:
    -----------
    oil_density : float
        Oil density (g/cc)
    water_density : float
        Water density (g/cc)
    drainage_radius : float
        Drainage radius (ft)
    wellbore_radius : float
        Radius of wellbore (ft)
    perforated_thickness : float
        Thickness of perforated interval (ft)
    oil_column_thickness : float
        Oil column thickness (ft)
    oil_viscosity : float
        Oil viscosity (cP)
    oil_fvf : float
        Oil formation volume factor (RB/STB)
    oil_permeability : float
        Effective oil permeability (mD)
        
    Returns:
    --------
    float
        Critical rate (STB/day)
        
    Reference:
    ----------
    Meyer, Gardner, and Pirson method for water coning.
    """
    import math
    
    term1 = 0.001535 * (water_density - oil_density) / math.log(drainage_radius / wellbore_radius)
    term2 = oil_permeability / (oil_viscosity * oil_fvf)
    term3 = oil_column_thickness**2 - (oil_column_thickness - perforated_thickness)**2
    
    return term1 * term2 * term3


def vertical_well_critical_rate_meyer_gardner_pirson_gas(
    oil_density: float,
    gas_density: float,
    drainage_radius: float,
    wellbore_radius: float,
    perforated_thickness: float,
    oil_column_thickness: float,
    oil_viscosity: float,
    oil_fvf: float,
    oil_permeability: float
) -> float:
    """
    Calculate critical rate using Meyer, Gardner, and Pirson method for gas coning only.
    
    Parameters:
    -----------
    oil_density : float
        Oil density (g/cc)
    gas_density : float
        Gas density (g/cc)
    drainage_radius : float
        Drainage radius (ft)
    wellbore_radius : float
        Radius of wellbore (ft)
    perforated_thickness : float
        Thickness of perforated interval (ft)
    oil_column_thickness : float
        Oil column thickness (ft)
    oil_viscosity: float
        Oil viscosity (cP)
    oil_fvf : float
        Oil formation volume factor (RB/STB)
    oil_permeability : float
        Effective oil permeability (mD)
        
    Returns:
    --------
    float
        Critical rate (STB/day)
        
    Reference:
    ----------
    Meyer, Gardner, and Pirson method for gas coning.
    """
    import math
    
    term1 = 0.001535 * (oil_density - gas_density) / math.log(drainage_radius / wellbore_radius)
    term2 = oil_permeability / (oil_viscosity * oil_fvf)
    term3 = oil_column_thickness**2 - (oil_column_thickness - perforated_thickness)**2
    
    return term1 * term2 * term3


def horizontal_well_critical_rate_chaperon(
    oil_permeability: float,
    thickness: float,
    density_difference: float,
    well_length: float,
    oil_viscosity: float,
    distance_to_boundary: float
) -> float:
    """
    Calculate horizontal well critical rate using Chaperon correlation.
    
    Parameters:
    -----------
    oil_permeability : float
        Oil permeability (mD)
    thickness : float
        Formation thickness (ft)
    density_difference : float
        Density difference between water and oil (g/cc)
    well_length : float
        Horizontal well length (ft)
    oil_viscosity : float
        Oil viscosity (cP)
    distance_to_boundary : float
        Distance to water contact (ft)
        
    Returns:
    --------
    float
        Critical rate (STB/day)
        
    Reference:
    ----------
    Chaperon correlation for horizontal well critical rate.
    """
    # Simplified Chaperon correlation
    qc = (0.00708 * oil_permeability * thickness**2 * density_difference * well_length) / \
         (oil_viscosity * distance_to_boundary)
    
    return qc


def horizontal_well_critical_rate_efros(
    permeability: float,
    thickness: float,
    density_difference: float,
    well_length: float,
    viscosity: float,
    anisotropy_ratio: float = 1.0
) -> float:
    """
    Calculate horizontal well critical rate using Efros correlation.
    
    Parameters:
    -----------
    permeability : float
        Horizontal permeability (mD)
    thickness : float
        Formation thickness (ft)
    density_difference : float
        Density difference (g/cc)
    well_length : float
        Well length (ft)
    viscosity : float
        Fluid viscosity (cP)
    anisotropy_ratio : float, optional
        Vertical to horizontal permeability ratio, default 1.0
        
    Returns:
    --------
    float
        Critical rate (STB/day)
        
    Reference:
    ----------
    Efros correlation for horizontal well critical rate.
    """
    # Efros correlation with anisotropy consideration
    effective_thickness = thickness * (anisotropy_ratio**0.5)
    
    qc = (0.00543 * permeability * effective_thickness**2 * density_difference * well_length) / viscosity
    
    return qc


def critical_rate_horizontal_well_chaperon(permeability_h, permeability_v, thickness, oil_density, water_density, well_length, formation_volume_factor):
    """
    Calculate horizontal well critical rate using Chaperon correlation.
    Formula 1.61 from additional_knowledge.tex
    
    Args:
        permeability_h (float): Horizontal permeability (md)
        permeability_v (float): Vertical permeability (md)
        thickness (float): Net pay thickness (ft)
        oil_density (float): Oil density (lbm/ft³)
        water_density (float): Water density (lbm/ft³)
        well_length (float): Horizontal well length (ft)
        formation_volume_factor (float): Oil formation volume factor (bbl/STB)
    
    Returns:
        float: Critical rate (STB/day)
    """
    import math
    
    # Density difference
    delta_rho = water_density - oil_density
    
    # Anisotropy ratio
    anisotropy_ratio = math.sqrt(permeability_v / permeability_h)
    
    # Chaperon correlation
    qc = 2.94e-6 * permeability_h * thickness**2 * delta_rho * anisotropy_ratio / (formation_volume_factor * well_length)
    
    return qc

def critical_rate_horizontal_well_efros(permeability_h, permeability_v, thickness, oil_density, water_density, viscosity, formation_volume_factor):
    """
    Calculate horizontal well critical rate using Efros correlation.
    Formula 1.62 from additional_knowledge.tex
    
    Args:
        permeability_h (float): Horizontal permeability (md)
        permeability_v (float): Vertical permeability (md)
        thickness (float): Net pay thickness (ft)
        oil_density (float): Oil density (lbm/ft³)
        water_density (float): Water density (lbm/ft³)
        viscosity (float): Oil viscosity (cp)
        formation_volume_factor (float): Oil formation volume factor (bbl/STB)
    
    Returns:
        float: Critical rate (STB/day)
    """
    import math
    
    # Density difference
    delta_rho = water_density - oil_density
    
    # Efros correlation
    qc = 4.9e-7 * permeability_h * permeability_v * thickness**2 * delta_rho / (viscosity * formation_volume_factor)
    
    return qc

def critical_rate_horizontal_well_giger_karcher(permeability_h, permeability_v, thickness, oil_density, water_density, viscosity, porosity, well_length):
    """
    Calculate horizontal well critical rate using Giger and Karcher correlation.
    Formula 1.63 from additional_knowledge.tex
    
    Args:
        permeability_h (float): Horizontal permeability (md)
        permeability_v (float): Vertical permeability (md)
        thickness (float): Net pay thickness (ft)
        oil_density (float): Oil density (lbm/ft³)
        water_density (float): Water density (lbm/ft³)
        viscosity (float): Oil viscosity (cp)
        porosity (float): Porosity (fraction)
        well_length (float): Horizontal well length (ft)
    
    Returns:
        float: Critical rate (STB/day)
    """
    import math
    
    # Density difference
    delta_rho = water_density - oil_density
    
    # Anisotropy ratio
    anisotropy_ratio = math.sqrt(permeability_v / permeability_h)
    
    # Giger and Karcher correlation
    qc = 6.28e-7 * permeability_h * thickness**2 * delta_rho * anisotropy_ratio / (viscosity * porosity * well_length)
    
    return qc

def critical_rate_horizontal_well_edge_water_drive(permeability, thickness, oil_density, water_density, viscosity, drainage_area, distance_to_edge):
    """
    Calculate critical rate for horizontal wells in edge-water drive reservoirs.
    Formula 1.16 from additional_knowledge.tex
    
    Args:
        permeability (float): Permeability (md)
        thickness (float): Net pay thickness (ft)
        oil_density (float): Oil density (lbm/ft³)
        water_density (float): Water density (lbm/ft³)
        viscosity (float): Oil viscosity (cp)
        drainage_area (float): Drainage area (acres)
        distance_to_edge (float): Distance to reservoir edge (ft)
    
    Returns:
        float: Critical rate (STB/day)
    """
    import math
    
    # Density difference
    delta_rho = water_density - oil_density
    
    # Convert drainage area to ft²
    area_ft2 = drainage_area * 43560  # acres to ft²
    
    # Critical rate correlation for edge-water drive
    qc = 7.08e-6 * permeability * thickness**2 * delta_rho * math.sqrt(area_ft2) / (viscosity * distance_to_edge)
    
    return qc

def water_breakthrough_sobocinski_cornelius(permeability, porosity, thickness, oil_viscosity, water_viscosity, initial_water_saturation, residual_oil_saturation, drainage_radius, wellbore_radius):
    """
    Calculate water breakthrough correlations using Sobocinski and Cornelius method.
    Formula 1.152 from additional_knowledge.tex
    
    Args:
        permeability (float): Permeability (md)
        porosity (float): Porosity (fraction)
        thickness (float): Net pay thickness (ft)
        oil_viscosity (float): Oil viscosity (cp)
        water_viscosity (float): Water viscosity (cp)
        initial_water_saturation (float): Initial water saturation (fraction)
        residual_oil_saturation (float): Residual oil saturation (fraction)
        drainage_radius (float): Drainage radius (ft)
        wellbore_radius (float): Wellbore radius (ft)
    
    Returns:
        dict: Dictionary containing breakthrough time and related parameters
    """
    import math
    
    # Mobility ratio
    mobility_ratio = (permeability / oil_viscosity) / (permeability / water_viscosity)
    
    # Movable oil saturation
    movable_oil_saturation = 1.0 - initial_water_saturation - residual_oil_saturation
    
    # Breakthrough time factor
    breakthrough_factor = porosity * movable_oil_saturation * math.log(drainage_radius / wellbore_radius) / (4 * permeability)
    
    return {
        'mobility_ratio': mobility_ratio,
        'movable_oil_saturation': movable_oil_saturation,
        'breakthrough_factor': breakthrough_factor
    }

def water_drive_recovery_efficiency(initial_oil_saturation, residual_oil_saturation, water_saturation_at_abandonment):
    """
    Calculate water-drive recovery efficiency.
    Formula 1.156 from additional_knowledge.tex
    
    Args:
        initial_oil_saturation (float): Initial oil saturation (fraction)
        residual_oil_saturation (float): Residual oil saturation (fraction)
        water_saturation_at_abandonment (float): Water saturation at abandonment (fraction)
    
    Returns:
        float: Recovery efficiency (fraction)
    """
    # Water-drive recovery efficiency
    recovery_efficiency = (initial_oil_saturation - residual_oil_saturation) / initial_oil_saturation
    
    # Account for water saturation at abandonment
    if water_saturation_at_abandonment > 0:
        effective_recovery = recovery_efficiency * (1.0 - water_saturation_at_abandonment)
        return effective_recovery
    
    return recovery_efficiency

def effective_wellbore_radius_horizontal_anisotropic(wellbore_radius, permeability_h, permeability_v, well_length):
    """
    Calculate effective wellbore radius of horizontal well in anisotropic reservoirs - Method 1.
    Formula 1.29 from additional_knowledge.tex
    
    Args:
        wellbore_radius (float): Actual wellbore radius (ft)
        permeability_h (float): Horizontal permeability (md)
        permeability_v (float): Vertical permeability (md)
        well_length (float): Horizontal well length (ft)
    
    Returns:
        float: Effective wellbore radius (ft)
    """
    import math
    
    # Anisotropy ratio
    anisotropy_ratio = math.sqrt(permeability_v / permeability_h)
    
    # Effective wellbore radius for anisotropic reservoir
    rw_eff = wellbore_radius * math.exp(-2 * anisotropy_ratio * well_length / (4 * wellbore_radius))
    
    return rw_eff

def effective_wellbore_radius_horizontal_isotropic(wellbore_radius, well_length, thickness):
    """
    Calculate effective wellbore radius of horizontal well in isotropic reservoirs - Method 1.
    Formula 1.30 from additional_knowledge.tex
    
    Args:
        wellbore_radius (float): Actual wellbore radius (ft)
        well_length (float): Horizontal well length (ft)
        thickness (float): Reservoir thickness (ft)
    
    Returns:
        float: Effective wellbore radius (ft)
    """
    import math
    
    # Effective wellbore radius for isotropic reservoir
    rw_eff = 2 * well_length / (math.pi * math.log(thickness / wellbore_radius))
    
    return rw_eff

def effective_wellbore_radius_van_der_vlis(wellbore_radius, well_length, thickness, permeability_h, permeability_v):
    """
    Calculate effective wellbore radius using van der Vlis et al. method.
    Formula 1.31 from additional_knowledge.tex
    
    Args:
        wellbore_radius (float): Actual wellbore radius (ft)
        well_length (float): Horizontal well length (ft)
        thickness (float): Reservoir thickness (ft)
        permeability_h (float): Horizontal permeability (md)
        permeability_v (float): Vertical permeability (md)
    
    Returns:
        float: Effective wellbore radius (ft)
    """
    import math
    
    # Anisotropy ratio
    anisotropy_ratio = math.sqrt(permeability_v / permeability_h)
    
    # van der Vlis correlation
    beta = 2 * math.pi * thickness / well_length
    rw_eff = wellbore_radius * beta / (2 * math.sinh(beta * anisotropy_ratio))
    
    return rw_eff

def effective_wellbore_radius_uniform_flux_fractures(wellbore_radius, fracture_half_length, number_of_fractures):
    """
    Calculate effective wellbore radius in presence of uniform-flux fractures.
    Formula 1.32 from additional_knowledge.tex
    
    Args:
        wellbore_radius (float): Actual wellbore radius (ft)
        fracture_half_length (float): Fracture half-length (ft)
        number_of_fractures (int): Number of fractures
    
    Returns:
        float: Effective wellbore radius (ft)
    """
    import math
    
    # Effective wellbore radius with fractures
    rw_eff = wellbore_radius * math.exp(number_of_fractures * fracture_half_length / (2 * wellbore_radius))
    
    return rw_eff

def effective_wellbore_radius_slant_well_van_der_vlis(wellbore_radius, slant_angle, thickness, permeability_h, permeability_v):
    """
    Calculate effective wellbore radius for slant well productivity using van der Vlis et al.
    Formula 1.33 from additional_knowledge.tex
    
    Args:
        wellbore_radius (float): Actual wellbore radius (ft)
        slant_angle (float): Slant angle from vertical (degrees)
        thickness (float): Reservoir thickness (ft)
        permeability_h (float): Horizontal permeability (md)
        permeability_v (float): Vertical permeability (md)
    
    Returns:
        float: Effective wellbore radius (ft)
    """
    import math
    
    # Convert angle to radians
    angle_rad = math.radians(slant_angle)
    
    # Anisotropy ratio
    anisotropy_ratio = math.sqrt(permeability_v / permeability_h)
    
    # Effective wellbore radius for slant well
    correction_factor = math.cos(angle_rad) + anisotropy_ratio * math.sin(angle_rad)
    rw_eff = wellbore_radius / correction_factor
    
    return rw_eff

def average_reservoir_pressure_mdh(pressure_buildup_data, time_data, permeability, porosity, viscosity, total_compressibility, drainage_area):
    """
    Estimate average reservoir pressure using MDH (Miller-Dyes-Hutchinson) method.
    Formula 1.34 from additional_knowledge.tex
    
    Args:
        pressure_buildup_data (list): Pressure buildup data (psia)
        time_data (list): Time data (hours)
        permeability (float): Permeability (md)
        porosity (float): Porosity (fraction)
        viscosity (float): Fluid viscosity (cp)
        total_compressibility (float): Total compressibility (1/psi)
        drainage_area (float): Drainage area (acres)
    
    Returns:
        dict: Dictionary containing average pressure and related parameters
    """
    import math
    
    # Convert drainage area to ft²
    area_ft2 = drainage_area * 43560
    
    # Calculate dimensionless time
    if len(time_data) > 0 and len(pressure_buildup_data) > 0:
        max_time = max(time_data)
        td = 0.0002637 * permeability * max_time / (porosity * viscosity * total_compressibility * area_ft2)
        
        # Estimate average pressure (simplified MDH approach)
        pressure_extrapolated = pressure_buildup_data[-1]  # Use last pressure point
        average_pressure = pressure_extrapolated + (pressure_buildup_data[0] - pressure_buildup_data[-1]) / (2 * math.log(td))
        
        return {
            'average_pressure': average_pressure,
            'dimensionless_time': td,
            'pressure_extrapolated': pressure_extrapolated
        }
    
    return {'error': 'Insufficient data'}

def gas_flow_rate_into_wellbore(permeability, thickness, pressure_reservoir, pressure_wellbore, gas_viscosity, gas_formation_volume_factor, drainage_radius, wellbore_radius):
    """
    Calculate gas flow rate into the wellbore.
    Formula 1.46 from additional_knowledge.tex
    
    Args:
        permeability (float): Permeability (md)
        thickness (float): Net pay thickness (ft)
        pressure_reservoir (float): Reservoir pressure (psia)
        pressure_wellbore (float): Wellbore pressure (psia)
        gas_viscosity (float): Gas viscosity (cp)
        gas_formation_volume_factor (float): Gas formation volume factor (bbl/scf)
        drainage_radius (float): Drainage radius (ft)
        wellbore_radius (float): Wellbore radius (ft)
    
    Returns:
        float: Gas flow rate (Mscf/day)
    """
    import math
    
    # Pressure squared difference for gas flow
    pressure_diff_squared = pressure_reservoir**2 - pressure_wellbore**2
    
    # Gas flow rate equation
    qg = 7.08e-3 * permeability * thickness * pressure_diff_squared / (gas_viscosity * gas_formation_volume_factor * math.log(drainage_radius / wellbore_radius))
    
    return qg / 1000  # Convert to Mscf/day

def horizontal_well_breakthrough_time(permeability, porosity, water_viscosity, oil_viscosity, initial_oil_saturation, well_length, distance_to_water_contact):
    """
    Calculate horizontal well breakthrough time with gas cap or bottom water.
    Formula 1.60 from additional_knowledge.tex
    
    Args:
        permeability (float): Permeability (md)
        porosity (float): Porosity (fraction)
        water_viscosity (float): Water viscosity (cp)
        oil_viscosity (float): Oil viscosity (cp)
        initial_oil_saturation (float): Initial oil saturation (fraction)
        well_length (float): Horizontal well length (ft)
        distance_to_water_contact (float): Distance to water contact (ft)
    
    Returns:
        float: Breakthrough time (days)
    """
    import math
    
    # Mobility ratio
    mobility_ratio = (permeability / water_viscosity) / (permeability / oil_viscosity)
    
    # Breakthrough time calculation
    breakthrough_time = porosity * initial_oil_saturation * distance_to_water_contact**2 / (4 * permeability * mobility_ratio * well_length)
    
    return breakthrough_time

def welge_extension_fractional_flow(water_saturation, relative_permeability_water, relative_permeability_oil, water_viscosity, oil_viscosity):
    """
    Calculate Welge extension for fractional flow.
    Formula 1.163 from additional_knowledge.tex
    
    Args:
        water_saturation (float): Water saturation (fraction)
        relative_permeability_water (float): Relative permeability to water
        relative_permeability_oil (float): Relative permeability to oil
        water_viscosity (float): Water viscosity (cp)
        oil_viscosity (float): Oil viscosity (cp)
    
    Returns:
        dict: Dictionary containing fractional flow and derivative
    """
    # Mobility ratio
    lambda_w = relative_permeability_water / water_viscosity
    lambda_o = relative_permeability_oil / oil_viscosity
    
    # Fractional flow of water
    fw = lambda_w / (lambda_w + lambda_o)
    
    # Derivative of fractional flow (simplified approximation)
    dfw_dsw = fw * (1 - fw) * (1 / water_saturation)  # Approximate derivative
    
    return {
        'fractional_flow_water': fw,
        'fractional_flow_derivative': dfw_dsw,
        'mobility_water': lambda_w,
        'mobility_oil': lambda_o
    }

def acid_penetration_distance(
    average_fracture_width: float,
    dimensionless_penetration_distance: float,
    reynolds_number: float,
    reynolds_number_fluid_loss: float
) -> float:
    """
    Calculates acid penetration distance during acidizing operations.
    
    Args:
        average_fracture_width (float): Average fracture width (ft)
        dimensionless_penetration_distance (float): Dimensionless acid penetration distance (dimensionless)
        reynolds_number (float): Reynolds number (dimensionless)
        reynolds_number_fluid_loss (float): Reynolds number for fluid loss (dimensionless)
        
    Returns:
        float: Acid penetration distance (ft)
        
    Reference:
        Chapter 4, Formula 4.1
    """
    return average_fracture_width * dimensionless_penetration_distance


def additional_pressure_drop_skin_zone(
    flow_rate: float,
    skin_factor: float,
    permeability: float,
    thickness: float,
    formation_volume_factor: float,
    viscosity: float
) -> float:
    """
    Calculates additional pressure drop in the skin zone.
    
    Args:
        flow_rate (float): Flow rate (STB/day)
        skin_factor (float): Skin factor (dimensionless)
        permeability (float): Permeability (mD)
        thickness (float): Formation thickness (ft)
        formation_volume_factor (float): Formation volume factor (RB/STB)
        viscosity (float): Viscosity (cP)
        
    Returns:
        float: Additional pressure drop (psi)
        
    Reference:
        Chapter 4, Formula 4.2
    """
    return (141.2 * flow_rate * formation_volume_factor * viscosity * skin_factor) / (permeability * thickness)


def brine_density_completion_fluid(
    specific_gravity_water: float,
    salt_concentration: float,
    temperature: float = 60.0
) -> float:
    """
    Calculates density of brine for completion and workover fluids.
    
    Args:
        specific_gravity_water (float): Specific gravity of water (dimensionless)
        salt_concentration (float): Salt concentration (weight fraction)
        temperature (float, optional): Temperature (°F). Defaults to 60.0.
        
    Returns:
        float: Brine density (ppg)
        
    Reference:
        Chapter 4, Formula 4.23
    """
    base_density = specific_gravity_water * 8.34  # ppg
    return base_density * (1 + 0.695 * salt_concentration)


def choke_discharge_coefficient(
    flow_rate: float,
    choke_area: float,
    upstream_pressure: float,
    downstream_pressure: float,
    fluid_density: float
) -> float:
    """
    Calculates choke discharge coefficient.
    
    Args:
        flow_rate (float): Flow rate (bbl/day)
        choke_area (float): Choke area (in²)
        upstream_pressure (float): Upstream pressure (psi)
        downstream_pressure (float): Downstream pressure (psi)
        fluid_density (float): Fluid density (lb/ft³)
        
    Returns:
        float: Discharge coefficient (dimensionless)
        
    Reference:
        Chapter 4, Formula 4.16
    """
    pressure_drop = upstream_pressure - downstream_pressure
    velocity_factor = math.sqrt(2 * 32.174 * pressure_drop * 144 / fluid_density)
    actual_velocity = (flow_rate * 5.615) / (choke_area * 86400 / 144)  # Convert to ft/s
    
    return actual_velocity / velocity_factor


def convective_mass_transfer_laminar_acidizing(
    diffusivity: float,
    velocity: float,
    pipe_diameter: float,
    length: float
) -> float:
    """
    Calculates convective mass transfer for laminar flow during acidizing.
    
    Args:
        diffusivity (float): Molecular diffusivity (ft²/s)
        velocity (float): Fluid velocity (ft/s)
        pipe_diameter (float): Pipe diameter (ft)
        length (float): Length (ft)
        
    Returns:
        float: Mass transfer coefficient (ft/s)
        
    Reference:
        Chapter 4, Formula 4.18
    """
    reynolds_equiv = velocity * pipe_diameter / diffusivity
    schmidt_number = 1.0  # Assumed for acid solutions
    sherwood_number = 1.86 * (reynolds_equiv * schmidt_number * pipe_diameter / length)**(1/3)
    
    return sherwood_number * diffusivity / pipe_diameter


def convective_mass_transfer_turbulent_acidizing(
    diffusivity: float,
    velocity: float,
    pipe_diameter: float,
    viscosity: float,
    density: float
) -> float:
    """
    Calculates convective mass transfer for turbulent flow during acidizing.
    
    Args:
        diffusivity (float): Molecular diffusivity (ft²/s)
        velocity (float): Fluid velocity (ft/s)
        pipe_diameter (float): Pipe diameter (ft)
        viscosity (float): Viscosity (lb/ft·s)
        density (float): Density (lb/ft³)
        
    Returns:
        float: Mass transfer coefficient (ft/s)
        
    Reference:
        Chapter 4, Formula 4.19
    """
    reynolds_number = density * velocity * pipe_diameter / viscosity
    schmidt_number = viscosity / (density * diffusivity)
    sherwood_number = 0.023 * reynolds_number**0.8 * schmidt_number**0.33
    
    return sherwood_number * diffusivity / pipe_diameter


def dimensionless_fracture_width_linear_vertical(
    fracture_width: float,
    fracture_height: float,
    elastic_modulus: float,
    net_pressure: float,
    poisson_ratio: float
) -> float:
    """
    Calculates dimensionless fracture width for linear vertical fracture.
    
    Args:
        fracture_width (float): Fracture width (ft)
        fracture_height (float): Fracture height (ft)
        elastic_modulus (float): Elastic modulus (psi)
        net_pressure (float): Net pressure (psi)
        poisson_ratio (float): Poisson's ratio (dimensionless)
        
    Returns:
        float: Dimensionless fracture width (dimensionless)
        
    Reference:
        Chapter 4, Formula 4.24
    """
    plane_strain_modulus = elastic_modulus / (1 - poisson_ratio**2)
    return (fracture_width * plane_strain_modulus) / (net_pressure * fracture_height)


def entrance_hole_size_perforation(
    gun_diameter: float,
    charge_diameter: float,
    standoff_distance: float
) -> float:
    """
    Calculates entrance hole size for perforation.
    
    Args:
        gun_diameter (float): Gun diameter (in.)
        charge_diameter (float): Charge diameter (in.)
        standoff_distance (float): Standoff distance (in.)
        
    Returns:
        float: Entrance hole diameter (in.)
        
    Reference:
        Chapter 4, Formula 4.26
    """
    return 0.25 * charge_diameter * (1 + gun_diameter / standoff_distance)


def equivalent_skin_factor_fractured_wells(
    fracture_half_length: float,
    wellbore_radius: float,
    horizontal_permeability: float,
    vertical_permeability: float,
    fracture_conductivity: float,
    formation_thickness: float,
    fracture_height: float
) -> float:
    """
    Calculates equivalent skin factor in fractured wells.
    
    Args:
        fracture_half_length (float): Fracture half-length (ft)
        wellbore_radius (float): Wellbore radius (ft)
        horizontal_permeability (float): Horizontal permeability (mD)
        vertical_permeability (float): Vertical permeability (mD)
        fracture_conductivity (float): Fracture conductivity (mD·ft)
        formation_thickness (float): Formation thickness (ft)
        fracture_height (float): Fracture height (ft)
        
    Returns:
        float: Equivalent skin factor (dimensionless)
        
    Reference:
        Chapter 4, Formula 4.27
    """
    term1 = math.log(fracture_half_length / wellbore_radius)
    term2 = math.log(math.sqrt(horizontal_permeability / vertical_permeability))
    term3 = (math.pi * horizontal_permeability * formation_thickness) / (2 * fracture_conductivity)
    
    return term1 + term2 - term3


def flow_coefficient_drawdown(
    flow_rate: float,
    pressure_drop: float,
    flow_exponent: float = 0.5
) -> float:
    """
    Calculates flow coefficient during drawdown.
    
    Args:
        flow_rate (float): Flow rate (Mscf/day for gas, STB/day for oil)
        pressure_drop (float): Pressure drop (psi² for gas, psi for oil)
        flow_exponent (float, optional): Flow exponent. Defaults to 0.5.
        
    Returns:
        float: Flow coefficient (Mscf/day/psi^n for gas, STB/day/psi for oil)
        
    Reference:
        Chapter 4, Formula 4.29
    """
    return flow_rate / (pressure_drop**flow_exponent)


def flow_rate_through_orifice(
    discharge_coefficient: float,
    orifice_area: float,
    pressure_drop: float,
    fluid_density: float
) -> float:
    """
    Calculates flow rate through orifice.
    
    Args:
        discharge_coefficient (float): Discharge coefficient (dimensionless)
        orifice_area (float): Orifice area (ft²)
        pressure_drop (float): Pressure drop across orifice (lbf/ft²)
        fluid_density (float): Fluid density (lb/ft³)
        
    Returns:
        float: Flow rate (ft³/s)
        
    Reference:
        Chapter 4, Formula 4.30
    """
    return discharge_coefficient * orifice_area * math.sqrt(2 * 32.174 * pressure_drop / fluid_density)


def fracture_gradient_hydraulic_fracturing(
    overburden_pressure: float,
    pore_pressure: float,
    poisson_ratio: float,
    biot_coefficient: float = 1.0
) -> float:
    """
    Calculates fracture gradient for hydraulic fracturing.
    
    Args:
        overburden_pressure (float): Overburden pressure (psi)
        pore_pressure (float): Pore pressure (psi)
        poisson_ratio (float): Poisson's ratio (dimensionless)
        biot_coefficient (float, optional): Biot coefficient. Defaults to 1.0.
        
    Returns:
        float: Fracture gradient (psi/ft)
        
    Reference:
        Chapter 4, Formula 4.38
    """
    stress_ratio = poisson_ratio / (1 - poisson_ratio)
    effective_stress = overburden_pressure - biot_coefficient * pore_pressure
    
    return pore_pressure + stress_ratio * effective_stress


def hydraulic_fracture_efficiency(
    net_pressure: float,
    fracture_height: float,
    fracture_length: float,
    injected_volume: float,
    leak_off_coefficient: float,
    injection_time: float
) -> float:
    """
    Calculates hydraulic fracture efficiency.
    
    Args:
        net_pressure (float): Net pressure (psi)
        fracture_height (float): Fracture height (ft)
        fracture_length (float): Fracture length (ft)
        injected_volume (float): Injected volume (bbl)
        leak_off_coefficient (float): Leak-off coefficient (ft/√min)
        injection_time (float): Injection time (min)
        
    Returns:
        float: Fracture efficiency (fraction)
        
    Reference:
        Chapter 4, Formula 4.42
    """
    fracture_volume = net_pressure * fracture_height * fracture_length / 5.615  # Convert to bbl
    leak_off_volume = 2 * leak_off_coefficient * fracture_height * fracture_length * math.sqrt(injection_time) / 5.615
    
    return fracture_volume / (fracture_volume + leak_off_volume)


def minimum_polished_rod_load_sucker_rod(
    fluid_load: float,
    rod_weight: float,
    buoyancy_factor: float
) -> float:
    """
    Calculates minimum polished rod load for sucker rod pump.
    
    Args:
        fluid_load (float): Fluid load (lbf)
        rod_weight (float): Rod weight in air (lbf)
        buoyancy_factor (float): Buoyancy factor (dimensionless)
        
    Returns:
        float: Minimum polished rod load (lbf)
        
    Reference:
        Chapter 4, Formula 4.53
    """
    return rod_weight * buoyancy_factor - fluid_load


def perforation_friction_factor(
    reynolds_number: float,
    relative_roughness: float
) -> float:
    """
    Calculates perforation friction factor.
    
    Args:
        reynolds_number (float): Reynolds number (dimensionless)
        relative_roughness (float): Relative roughness (dimensionless)
        
    Returns:
        float: Friction factor (dimensionless)
        
    Reference:
        Chapter 4, Formula 4.55
    """
    if reynolds_number < 2300:
        # Laminar flow
        return 64 / reynolds_number
    else:
        # Turbulent flow - Colebrook equation (simplified)
        return 0.25 / (math.log10(relative_roughness / 3.7 + 5.74 / reynolds_number**0.9))**2


def pressure_drop_perforations_gas_wells(
    gas_flow_rate: float,
    gas_specific_gravity: float,
    temperature: float,
    perforation_diameter: float,
    number_perforations: float,
    wellbore_pressure: float
) -> float:
    """
    Calculates pressure drop across perforations in gas wells.
    
    Args:
        gas_flow_rate (float): Gas flow rate (Mscf/day)
        gas_specific_gravity (float): Gas specific gravity (dimensionless)
        temperature (float): Temperature (°R)
        perforation_diameter (float): Perforation diameter (in.)
        number_perforations (float): Number of perforations (count)
        wellbore_pressure (float): Wellbore pressure (psi)
        
    Returns:
        float: Pressure drop (psi)
        
    Reference:
        Chapter 4, Formula 4.62
    """
    perforation_area = number_perforations * math.pi * (perforation_diameter / 24)**2  # ft²
    gas_density = (2.7 * gas_specific_gravity * wellbore_pressure) / temperature  # lb/ft³
    
    velocity = (gas_flow_rate * 1000) / (86400 * perforation_area)  # ft/s
    
    return gas_density * velocity**2 / (2 * 32.174 * 144)  # Convert to psi


def productivity_ratio_fractured_formation(
    fractured_productivity_index: float,
    unfractured_productivity_index: float
) -> float:
    """
    Calculates productivity ratio for hydraulically-fractured formation.
    
    Args:
        fractured_productivity_index (float): Productivity index after fracturing (STB/day/psi)
        unfractured_productivity_index (float): Productivity index before fracturing (STB/day/psi)
        
    Returns:
        float: Productivity ratio (dimensionless)
        
    Reference:
        Chapter 4, Formula 4.69
    """
    return fractured_productivity_index / unfractured_productivity_index


def single_phase_gas_flow_subsonic(
    flow_coefficient: float,
    upstream_pressure: float,
    downstream_pressure: float,
    temperature: float,
    gas_specific_gravity: float,
    choke_diameter: float
) -> float:
    """
    Calculates single-phase gas flow rate (subsonic) through choke.
    
    Args:
        flow_coefficient (float): Flow coefficient (dimensionless)
        upstream_pressure (float): Upstream pressure (psia)
        downstream_pressure (float): Downstream pressure (psia)
        temperature (float): Temperature (°R)
        gas_specific_gravity (float): Gas specific gravity (dimensionless)
        choke_diameter (float): Choke diameter (in.)
        
    Returns:
        float: Gas flow rate (Mscf/day)
        
    Reference:
        Chapter 4, Formula 4.81
    """
    choke_area = math.pi * (choke_diameter / 2)**2  # in²
    pressure_ratio = downstream_pressure / upstream_pressure
    
    if pressure_ratio > 0.5:
        # Subsonic flow
        flow_factor = math.sqrt(pressure_ratio**(2/1.4) - pressure_ratio**(2.4/1.4))
    else:
        # Critical flow
        flow_factor = 0.484
    
    return 520 * flow_coefficient * choke_area * upstream_pressure * flow_factor / math.sqrt(gas_specific_gravity * temperature)


def skin_factor_hawkins_method(
    damaged_zone_permeability: float,
    undamaged_zone_permeability: float,
    damaged_zone_radius: float,
    wellbore_radius: float
) -> float:
    """
    Calculates skin factor using Hawkins method.
    
    Args:
        damaged_zone_permeability (float): Permeability in damaged zone (mD)
        undamaged_zone_permeability (float): Permeability in undamaged zone (mD)
        damaged_zone_radius (float): Radius of damaged zone (ft)
        wellbore_radius (float): Wellbore radius (ft)
        
    Returns:
        float: Skin factor (dimensionless)
        
    Reference:
        Chapter 4, Formula 4.84
    """
    permeability_ratio = undamaged_zone_permeability / damaged_zone_permeability
    radius_ratio = damaged_zone_radius / wellbore_radius
    
    return (permeability_ratio - 1) * math.log(radius_ratio)


def wellbore_storage_coefficient(
    wellbore_volume: float,
    fluid_compressibility: float
) -> float:
    """
    Calculates wellbore storage coefficient.
    
    Args:
        wellbore_volume (float): Wellbore volume (bbl)
        fluid_compressibility (float): Fluid compressibility (1/psi)
        
    Returns:
        float: Wellbore storage coefficient (bbl/psi)
        
    Reference:
        Chapter 4, Formula 4.111
    """
    return wellbore_volume * fluid_compressibility
