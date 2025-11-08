"""
Flow calculations for petroleum engineering.

This module contains functions for flow calculations including:
- Single-phase and multiphase flow
- Flow through pipes and restrictions
- Choke flow calculations
- Flow in porous media
"""

import math
from typing import Union, Tuple, Optional


def moody_friction_factor(reynolds_number: float, relative_roughness: float) -> float:
    """
    Calculates friction factor using Moody chart correlation.
    
    Args:
        reynolds_number (float): Reynolds number (dimensionless)
        relative_roughness (float): Relative roughness (ε/D)
        
    Returns:
        float: Darcy friction factor (dimensionless)
    """
    re = reynolds_number
    roughness = relative_roughness
    
    if re < 2100:
        # Laminar flow
        f = 64 / re
    elif re < 4000:
        # Transition region (interpolation)
        f_lam = 64 / 2100
        f_turb = 0.0791 / (4000**0.25)
        f = f_lam + (f_turb - f_lam) * (re - 2100) / (4000 - 2100)
    else:
        # Turbulent flow - Colebrook-White equation (implicit)
        # Using approximation for computational efficiency
        if roughness == 0:
            # Smooth pipe - Blasius equation
            f = 0.0791 / (re**0.25)
        else:
            # Rough pipe - approximation
            f = 0.25 / (math.log10(roughness/3.7 + 5.74/(re**0.9)))**2
    
    return f


def pressure_drop_horizontal_pipe(
    flow_rate: float,
    pipe_diameter: float,
    pipe_length: float,
    fluid_density: float,
    fluid_viscosity: float,
    pipe_roughness: float = 0.0006
) -> float:
    """
    Calculates pressure drop in horizontal pipe due to friction.
    
    Args:
        flow_rate (float): Flow rate in bbl/day
        pipe_diameter (float): Pipe inner diameter in inches
        pipe_length (float): Pipe length in ft
        fluid_density (float): Fluid density in lb/ft³
        fluid_viscosity (float): Fluid viscosity in cp
        pipe_roughness (float): Pipe roughness in ft (default 0.0006)
        
    Returns:
        float: Pressure drop in psi
    """
    q = flow_rate / 86400  # Convert to ft³/sec
    d = pipe_diameter / 12  # Convert to ft
    l = pipe_length
    rho = fluid_density
    mu = fluid_viscosity
    roughness = pipe_roughness
    
    # Calculate velocity
    area = math.pi * d**2 / 4
    velocity = q / area  # ft/sec
    
    # Reynolds number
    re = rho * velocity * d / (mu * 6.72e-4)  # Convert viscosity units
    
    # Relative roughness
    rel_roughness = roughness / d
    
    # Friction factor
    f = moody_friction_factor(re, rel_roughness)
    
    # Pressure drop (Darcy-Weisbach equation)
    dp = f * (l / d) * (rho * velocity**2) / (2 * 32.174 * 144)  # psi
    
    return dp


def gas_flow_rate_weymouth(
    upstream_pressure: float,
    downstream_pressure: float,
    pipe_diameter: float,
    pipe_length: float,
    gas_gravity: float,
    temperature: float,
    efficiency: float = 1.0
) -> float:
    """
    Calculates gas flow rate using Weymouth equation.
    
    Args:
        upstream_pressure (float): Upstream pressure in psia
        downstream_pressure (float): Downstream pressure in psia
        pipe_diameter (float): Pipe inner diameter in inches
        pipe_length (float): Pipe length in miles
        gas_gravity (float): Gas specific gravity (air = 1.0)
        temperature (float): Average gas temperature in °R
        efficiency (float): Pipeline efficiency factor (default 1.0)
        
    Returns:
        float: Gas flow rate in Mscf/day
    """
    p1 = upstream_pressure
    p2 = downstream_pressure
    d = pipe_diameter
    l = pipe_length
    sg = gas_gravity
    t = temperature
    e = efficiency
    
    # Weymouth equation
    q = 433.5 * e * d**(8/3) * math.sqrt((p1**2 - p2**2) / (sg * t * l))
    
    return q


def oil_flow_rate_hazen_williams(
    pressure_drop: float,
    pipe_diameter: float,
    pipe_length: float,
    hazen_williams_coefficient: float = 120
) -> float:
    """
    Calculates oil flow rate using Hazen-Williams equation.
    
    Args:
        pressure_drop (float): Pressure drop in psi
        pipe_diameter (float): Pipe diameter in inches
        pipe_length (float): Pipe length in ft
        hazen_williams_coefficient (float): Hazen-Williams coefficient (default 120)
        
    Returns:
        float: Flow rate in bbl/day
    """
    dp = pressure_drop
    d = pipe_diameter
    l = pipe_length
    c = hazen_williams_coefficient
    
    # Hazen-Williams equation for oil
    q = 4.52 * c * d**2.63 * (dp / l)**0.54
    
    return q


def critical_flow_velocity(
    liquid_density: float,
    gas_density: float,
    surface_tension: float
) -> float:
    """
    Calculates critical velocity for liquid carryover in gas flow.
    
    Args:
        liquid_density (float): Liquid density in lb/ft³
        gas_density (float): Gas density in lb/ft³
        surface_tension (float): Surface tension in dynes/cm
        
    Returns:
        float: Critical velocity in ft/sec
    """
    rho_l = liquid_density
    rho_g = gas_density
    sigma = surface_tension / 1000  # Convert to lb/ft
    
    # Souders-Brown equation
    k = 0.35  # Typical K-factor for horizontal separators
    vc = k * math.sqrt((rho_l - rho_g) / rho_g)
    
    return vc


def terminal_settling_velocity(
    particle_diameter: float,
    particle_density: float,
    fluid_density: float,
    fluid_viscosity: float
) -> float:
    """
    Calculates terminal settling velocity of particles in fluid.
    
    Args:
        particle_diameter (float): Particle diameter in ft
        particle_density (float): Particle density in lb/ft³
        fluid_density (float): Fluid density in lb/ft³
        fluid_viscosity (float): Fluid viscosity in cp
        
    Returns:
        float: Terminal settling velocity in ft/sec
    """
    dp = particle_diameter
    rho_p = particle_density
    rho_f = fluid_density
    mu = fluid_viscosity * 6.72e-4  # Convert to lb/ft-sec
    
    # Gravity constant
    g = 32.174  # ft/sec²
    
    # Stokes law (for small particles)
    vt = (g * dp**2 * (rho_p - rho_f)) / (18 * mu)
    
    # Check Reynolds number for validity
    re = rho_f * vt * dp / mu
    
    if re > 0.5:
        # Use Newton's law for larger particles
        cd = 0.44  # Drag coefficient for spheres at high Re
        vt = math.sqrt((4 * g * dp * (rho_p - rho_f)) / (3 * cd * rho_f))
    
    return vt


def flow_through_orifice(
    upstream_pressure: float,
    downstream_pressure: float,
    orifice_diameter: float,
    fluid_density: float,
    discharge_coefficient: float = 0.6
) -> float:
    """
    Calculates flow rate through an orifice.
    
    Args:
        upstream_pressure (float): Upstream pressure in psi
        downstream_pressure (float): Downstream pressure in psi
        orifice_diameter (float): Orifice diameter in inches
        fluid_density (float): Fluid density in lb/ft³
        discharge_coefficient (float): Discharge coefficient (default 0.6)
        
    Returns:
        float: Flow rate in bbl/day
    """
    p1 = upstream_pressure * 144  # Convert to psf
    p2 = downstream_pressure * 144
    d = orifice_diameter / 12  # Convert to ft
    rho = fluid_density
    cd = discharge_coefficient
    
    # Orifice equation
    area = math.pi * d**2 / 4
    dp = p1 - p2
    
    if dp <= 0:
        return 0
    
    velocity = cd * math.sqrt(2 * 32.174 * dp / rho)
    q = area * velocity  # ft³/sec
    
    # Convert to bbl/day
    q_bbl_day = q * 86400 / 5.615
    
    return q_bbl_day


def multiphase_flow_pressure_drop(
    liquid_superficial_velocity: float,
    gas_superficial_velocity: float,
    pipe_diameter: float,
    pipe_inclination: float,
    liquid_density: float,
    gas_density: float,
    liquid_viscosity: float,
    gas_viscosity: float,
    surface_tension: float
) -> Tuple[float, float]:
    """
    Calculates pressure drop in multiphase flow using simplified correlation.
    
    Args:
        liquid_superficial_velocity (float): Liquid superficial velocity in ft/sec
        gas_superficial_velocity (float): Gas superficial velocity in ft/sec
        pipe_diameter (float): Pipe diameter in ft
        pipe_inclination (float): Pipe inclination in degrees from horizontal
        liquid_density (float): Liquid density in lb/ft³
        gas_density (float): Gas density in lb/ft³
        liquid_viscosity (float): Liquid viscosity in cp
        gas_viscosity (float): Gas viscosity in cp
        surface_tension (float): Surface tension in dynes/cm
        
    Returns:
        tuple: (pressure_gradient_psi_per_ft, liquid_holdup)
    """
    vsl = liquid_superficial_velocity
    vsg = gas_superficial_velocity
    d = pipe_diameter
    theta = math.radians(pipe_inclination)
    rho_l = liquid_density
    rho_g = gas_density
    mu_l = liquid_viscosity
    mu_g = gas_viscosity
    sigma = surface_tension
    
    # Mixture velocity
    vm = vsl + vsg
    
    # Liquid input holdup
    lambda_l = vsl / vm if vm > 0 else 0
    
    # Simplified liquid holdup correlation
    if lambda_l < 0.01:
        hl = lambda_l
    else:
        # Simplified correlation
        hl = 0.845 * lambda_l**0.5
    
    # Mixture density
    rho_m = hl * rho_l + (1 - hl) * rho_g
    
    # Friction factor calculation
    mu_m = hl * mu_l + (1 - hl) * mu_g
    re = rho_m * vm * d / (mu_m * 6.72e-4)
    
    if re < 2100:
        f = 64 / re
    else:
        f = 0.0791 / re**0.25
    
    # Pressure gradient components
    # Hydrostatic
    dp_dz_h = rho_m * math.sin(theta) / 144
    
    # Friction
    dp_dz_f = 2 * f * rho_m * vm**2 / (32.174 * d * 144)
    
    # Total pressure gradient
    dp_dz_total = dp_dz_h + dp_dz_f
    
    return dp_dz_total, hl


def pump_head_calculation(
    flow_rate: float,
    total_dynamic_head: float,
    pump_efficiency: float = 0.75
) -> float:
    """
    Calculates required pump power.
    
    Args:
        flow_rate (float): Flow rate in bbl/day
        total_dynamic_head (float): Total dynamic head in ft
        pump_efficiency (float): Pump efficiency fraction (default 0.75)
        
    Returns:
        float: Required pump power in hp
    """
    q = flow_rate / 86400  # Convert to ft³/sec
    h = total_dynamic_head
    eff = pump_efficiency
    
    # Specific weight of fluid (assume water)
    gamma = 62.4  # lb/ft³
    
    # Hydraulic power
    power_hydraulic = (gamma * q * h) / 550  # hp
    
    # Brake power
    power_brake = power_hydraulic / eff
    
    return power_brake


def hagen_poiseuille_flow(
    pressure_drop: float,
    pipe_diameter: float,
    pipe_length: float,
    fluid_viscosity: float
) -> float:
    """
    Calculates flow rate using Hagen-Poiseuille equation for laminar flow.
    
    Args:
        pressure_drop (float): Pressure drop (psi)
        pipe_diameter (float): Pipe diameter (inches)
        pipe_length (float): Pipe length (ft)
        fluid_viscosity (float): Fluid viscosity (cP)
        
    Returns:
        float: Flow rate (bbl/day)
        
    Reference:
        Hagen-Poiseuille equation for laminar flow in pipes
    """
    dp = pressure_drop * 144  # Convert psi to lb/ft²
    d = pipe_diameter / 12  # Convert inches to ft
    l = pipe_length
    mu = fluid_viscosity * 6.72e-4  # Convert cP to lb/ft·s
    
    # Hagen-Poiseuille equation
    q = (math.pi * d**4 * dp) / (128 * mu * l)  # ft³/s
    
    # Convert to bbl/day
    q_bbl_day = q * 86400 / 5.615
    
    return max(0, q_bbl_day)


def gas_flow_laminar_viscous(
    pressure_upstream: float,
    pressure_downstream: float,
    pipe_diameter: float,
    pipe_length: float,
    gas_viscosity: float,
    temperature: float,
    z_factor: float = 1.0
) -> float:
    """
    Calculates gas flow rate under laminar viscous conditions.
    
    Args:
        pressure_upstream (float): Upstream pressure (psia)
        pressure_downstream (float): Downstream pressure (psia)
        pipe_diameter (float): Pipe diameter (inches)
        pipe_length (float): Pipe length (ft)
        gas_viscosity (float): Gas viscosity (cP)
        temperature (float): Temperature (°R)
        z_factor (float): Gas compressibility factor (dimensionless), default 1.0
        
    Returns:
        float: Gas flow rate (MSCF/day)
        
    Reference:
        Laminar gas flow in pipes
    """
    p1 = pressure_upstream
    p2 = pressure_downstream
    d = pipe_diameter
    l = pipe_length
    mu = gas_viscosity
    t = temperature
    z = z_factor
    
    # Average pressure for property evaluation
    p_avg = (p1 + p2) / 2
    
    # Gas flow rate (simplified laminar flow equation)
    q = (math.pi * d**4 * (p1**2 - p2**2)) / (128 * mu * z * 10.732 * t * l)
    
    # Convert to MSCF/day
    q_mscf_day = q * 86400 / 1000
    
    return max(0, q_mscf_day)


def high_pressure_gas_flow_rate(
    permeability: float,
    thickness: float,
    pressure_reservoir: float,
    pressure_wellbore: float,
    drainage_radius: float,
    wellbore_radius: float,
    gas_viscosity: float,
    z_factor: float,
    temperature: float
) -> float:
    """
    Calculates gas flow rate in high-pressure region.
    
    Args:
        permeability (float): Permeability (mD)
        thickness (float): Net pay thickness (ft)
        pressure_reservoir (float): Reservoir pressure (psia)
        pressure_wellbore (float): Wellbore pressure (psia)
        drainage_radius (float): Drainage radius (ft)
        wellbore_radius (float): Wellbore radius (ft)
        gas_viscosity (float): Gas viscosity (cP)
        z_factor (float): Gas compressibility factor (dimensionless)
        temperature (float): Temperature (°R)
        
    Returns:
        float: Gas flow rate (MSCF/day)
        
    Reference:
        High-pressure gas flow calculations
    """
    k = permeability
    h = thickness
    pr = pressure_reservoir
    pwf = pressure_wellbore
    re = drainage_radius
    rw = wellbore_radius
    mu = gas_viscosity
    z = z_factor
    t = temperature
    
    # High-pressure gas flow equation
    q = (k * h * (pr**2 - pwf**2)) / (1422 * t * z * mu * math.log(re / rw))
    
    return max(0, q)


def low_pressure_gas_flow_rate(
    permeability: float,
    thickness: float,
    pressure_reservoir: float,
    pressure_wellbore: float,
    shape_factor: float,
    drainage_area: float,
    wellbore_radius: float,
    gas_viscosity: float,
    z_factor: float,
    temperature: float
) -> float:
    """
    Calculates gas flow rate in low-pressure region for non-circular drainage area.
    
    Args:
        permeability (float): Permeability (mD)
        thickness (float): Net pay thickness (ft)
        pressure_reservoir (float): Reservoir pressure (psia)
        pressure_wellbore (float): Wellbore pressure (psia)
        shape_factor (float): Shape factor for drainage area (dimensionless)
        drainage_area (float): Drainage area (acres)
        wellbore_radius (float): Wellbore radius (ft)
        gas_viscosity (float): Gas viscosity (cP)
        z_factor (float): Gas compressibility factor (dimensionless)
        temperature (float): Temperature (°R)
        
    Returns:
        float: Gas flow rate (MSCF/day)
        
    Reference:
        Low-pressure gas flow for non-circular drainage areas
    """
    k = permeability
    h = thickness
    pr = pressure_reservoir
    pwf = pressure_wellbore
    ca = shape_factor
    a = drainage_area
    rw = wellbore_radius
    mu = gas_viscosity
    z = z_factor
    t = temperature
    
    # Convert acres to ft²
    area_ft2 = a * 43560
    
    # Equivalent radius
    re = math.sqrt(area_ft2 / math.pi)
    
    # Low-pressure gas flow with shape factor
    q = (k * h * (pr**2 - pwf**2)) / (1422 * t * z * mu * (math.log(re / rw) - 0.75 + ca))
    
    return max(0, q)


def hagoort_hoogstra_tight_gas_flow(
    permeability: float,
    thickness: float,
    pressure_reservoir: float,
    pressure_wellbore: float,
    drainage_radius: float,
    wellbore_radius: float,
    gas_viscosity: float,
    gas_compressibility: float,
    temperature: float,
    non_darcy_coefficient: float = 0
) -> float:
    """
    Calculates gas flow in tight reservoirs using Hagoort and Hoogstra method.
    
    Args:
        permeability (float): Permeability (mD)
        thickness (float): Net pay thickness (ft)
        pressure_reservoir (float): Reservoir pressure (psia)
        pressure_wellbore (float): Wellbore pressure (psia)
        drainage_radius (float): Drainage radius (ft)
        wellbore_radius (float): Wellbore radius (ft)
        gas_viscosity (float): Gas viscosity (cP)
        gas_compressibility (float): Gas compressibility (1/psi)
        temperature (float): Temperature (°R)
        non_darcy_coefficient (float): Non-Darcy flow coefficient (1/ft), default 0
        
    Returns:
        float: Gas flow rate (MSCF/day)
        
    Reference:
        Hagoort and Hoogstra gas flow in tight reservoirs
    """
    k = permeability
    h = thickness
    pr = pressure_reservoir
    pwf = pressure_wellbore
    re = drainage_radius
    rw = wellbore_radius
    mu = gas_viscosity
    cg = gas_compressibility
    t = temperature
    beta = non_darcy_coefficient
    
    # Average pressure
    p_avg = (pr + pwf) / 2
    
    # Pseudo-pressure function for real gas
    m_pr = 2 * pr / (mu * cg)
    m_pwf = 2 * pwf / (mu * cg)
    
    # Flow rate including non-Darcy effects
    if beta > 0:
        # Non-Darcy flow correction
        q = (k * h * (m_pr - m_pwf)) / (1422 * t * (math.log(re / rw) + beta * k * h))
    else:
        # Standard Darcy flow
        q = (k * h * (m_pr - m_pwf)) / (1422 * t * math.log(re / rw))
    
    return max(0, q)


def kerns_gas_flow_fracture(
    fracture_conductivity: float,
    fracture_half_length: float,
    pressure_reservoir: float,
    pressure_wellbore: float,
    gas_viscosity: float,
    z_factor: float,
    temperature: float
) -> float:
    """
    Calculates gas flow rate in a fracture using Kerns method.
    
    Args:
        fracture_conductivity (float): Fracture conductivity (mD·ft)
        fracture_half_length (float): Fracture half-length (ft)
        pressure_reservoir (float): Reservoir pressure (psia)
        pressure_wellbore (float): Wellbore pressure (psia)
        gas_viscosity (float): Gas viscosity (cP)
        z_factor (float): Gas compressibility factor (dimensionless)
        temperature (float): Temperature (°R)
        
    Returns:
        float: Gas flow rate (MSCF/day)
        
    Reference:
        Kerns method for gas flow in fractured wells
    """
    kf_wf = fracture_conductivity
    xf = fracture_half_length
    pr = pressure_reservoir
    pwf = pressure_wellbore
    mu = gas_viscosity
    z = z_factor
    t = temperature
    
    # Kerns correlation for fractured gas wells
    q = (kf_wf * (pr**2 - pwf**2)) / (1422 * t * z * mu * xf)
    
    return max(0, q)


def gas_flow_into_wellbore(
    reservoir_pressure: float,
    wellbore_pressure: float,
    productivity_index: float,
    gas_formation_volume_factor: float
) -> float:
    """
    Calculates gas flow rate into the wellbore.
    
    Args:
        reservoir_pressure (float): Reservoir pressure (psia)
        wellbore_pressure (float): Wellbore pressure (psia)
        productivity_index (float): Gas well productivity index (MSCF/day/psi²)
        gas_formation_volume_factor (float): Gas formation volume factor (bbl/scf)
        
    Returns:
        float: Gas flow rate (MSCF/day)
        
    Reference:
        Gas well performance calculations
    """
    pr = reservoir_pressure
    pwf = wellbore_pressure
    pi = productivity_index
    bg = gas_formation_volume_factor
    
    # Gas flow rate using squared pressure difference
    q = pi * (pr**2 - pwf**2) / bg
    
    return max(0, q)


def interporosity_flow_coefficient(
    matrix_permeability: float,
    fracture_spacing: float,
    matrix_porosity: float,
    matrix_compressibility: float,
    fluid_viscosity: float
) -> float:
    """
    Calculates interporosity flow coefficient for dual porosity systems.
    
    Args:
        matrix_permeability (float): Matrix permeability (mD)
        fracture_spacing (float): Fracture spacing (ft)
        matrix_porosity (float): Matrix porosity (fraction)
        matrix_compressibility (float): Matrix compressibility (1/psi)
        fluid_viscosity (float): Fluid viscosity (cP)
        
    Returns:
        float: Interporosity flow coefficient (1/day)
        
    Reference:
        Dual porosity reservoir flow calculations
    """
    km = matrix_permeability
    l = fracture_spacing
    phi_m = matrix_porosity
    cm = matrix_compressibility
    mu = fluid_viscosity
    
    # Interporosity flow coefficient
    lambda_coeff = (12 * km) / (phi_m * cm * mu * l**2)
    
    return lambda_coeff


def archimedes_number(
    gravitational_acceleration: float,
    fluid_density: float,
    body_density: float,
    dynamic_viscosity: float,
    characteristic_length: float
) -> float:
    """
    Calculates Archimedes number for fluid-body interaction.
    
    Args:
        gravitational_acceleration (float): Local gravitational acceleration (m/s²)
        fluid_density (float): Density of the fluid (kg/m³)
        body_density (float): Density of the body (kg/m³)
        dynamic_viscosity (float): Dynamic viscosity (kg/(s·m))
        characteristic_length (float): Characteristic length of body (m)
        
    Returns:
        float: Archimedes number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.1
    """
    density_difference = abs(body_density - fluid_density)
    return (gravitational_acceleration * density_difference * fluid_density * characteristic_length**3) / dynamic_viscosity**2


def average_velocity_circular_tube(
    flow_rate: float,
    tube_diameter: float
) -> float:
    """
    Calculates average velocity of flow through a circular tube.
    
    Args:
        flow_rate (float): Volumetric flow rate (m³/s)
        tube_diameter (float): Tube diameter (m)
        
    Returns:
        float: Average velocity (m/s)
        
    Reference:
        Chapter 5, Formula 5.4
    """
    cross_sectional_area = math.pi * (tube_diameter / 2)**2
    return flow_rate / cross_sectional_area


def average_velocity_annulus(
    flow_rate: float,
    outer_diameter: float,
    inner_diameter: float
) -> float:
    """
    Calculates average velocity of flow through an annulus.
    
    Args:
        flow_rate (float): Volumetric flow rate (m³/s)
        outer_diameter (float): Outer diameter (m)
        inner_diameter (float): Inner diameter (m)
        
    Returns:
        float: Average velocity (m/s)
        
    Reference:
        Chapter 5, Formula 5.5
    """
    annular_area = math.pi * (outer_diameter**2 - inner_diameter**2) / 4
    return flow_rate / annular_area


def blowdown_time_unsteady_gas_flow(
    initial_pressure: float,
    final_pressure: float,
    vessel_volume: float,
    discharge_coefficient: float,
    orifice_area: float,
    gas_specific_heat_ratio: float,
    temperature: float,
    molecular_weight: float
) -> float:
    """
    Calculates blowdown time in unsteady gas flow.
    
    Args:
        initial_pressure (float): Initial pressure (Pa)
        final_pressure (float): Final pressure (Pa)
        vessel_volume (float): Vessel volume (m³)
        discharge_coefficient (float): Discharge coefficient (dimensionless)
        orifice_area (float): Orifice area (m²)
        gas_specific_heat_ratio (float): Specific heat ratio (γ) (dimensionless)
        temperature (float): Temperature (K)
        molecular_weight (float): Molecular weight (kg/kmol)
        
    Returns:
        float: Blowdown time (s)
        
    Reference:
        Chapter 5, Formula 5.8
    """
    gas_constant = 8314.3  # J/(kmol·K)
    sonic_velocity = math.sqrt(gas_specific_heat_ratio * gas_constant * temperature / molecular_weight)
    
    pressure_ratio = final_pressure / initial_pressure
    
    # Simplified blowdown calculation
    return (vessel_volume / (discharge_coefficient * orifice_area * sonic_velocity)) * \
           math.log(initial_pressure / final_pressure)


def brinkman_number(
    viscosity: float,
    velocity_gradient: float,
    thermal_conductivity: float,
    temperature_difference: float,
    characteristic_length: float
) -> float:
    """
    Calculates Brinkman number for viscous heating effects.
    
    Args:
        viscosity (float): Dynamic viscosity (Pa·s)
        velocity_gradient (float): Velocity gradient (1/s)
        thermal_conductivity (float): Thermal conductivity (W/(m·K))
        temperature_difference (float): Temperature difference (K)
        characteristic_length (float): Characteristic length (m)
        
    Returns:
        float: Brinkman number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.11
    """
    return (viscosity * velocity_gradient**2 * characteristic_length) / (thermal_conductivity * temperature_difference)


def darcy_weisbach_pressure_loss(
    friction_factor: float,
    pipe_length: float,
    pipe_diameter: float,
    fluid_density: float,
    velocity: float
) -> float:
    """
    Calculates pressure loss using Darcy-Weisbach equation.
    
    Args:
        friction_factor (float): Darcy friction factor (dimensionless)
        pipe_length (float): Pipe length (m)
        pipe_diameter (float): Pipe diameter (m)
        fluid_density (float): Fluid density (kg/m³)
        velocity (float): Average velocity (m/s)
        
    Returns:
        float: Pressure loss (Pa)
        
    Reference:
        Chapter 5, Formula 5.21
    """
    return friction_factor * (pipe_length / pipe_diameter) * (fluid_density * velocity**2) / 2


def dean_number(
    reynolds_number: float,
    tube_diameter: float,
    curvature_radius: float
) -> float:
    """
    Calculates Dean number for flow in curved pipes.
    
    Args:
        reynolds_number (float): Reynolds number (dimensionless)
        tube_diameter (float): Tube diameter (m)
        curvature_radius (float): Radius of curvature (m)
        
    Returns:
        float: Dean number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.22
    """
    return reynolds_number * math.sqrt(tube_diameter / (2 * curvature_radius))


def deborah_number(
    relaxation_time: float,
    observation_time: float
) -> float:
    """
    Calculates Deborah number for viscoelastic effects.
    
    Args:
        relaxation_time (float): Characteristic relaxation time (s)
        observation_time (float): Characteristic observation time (s)
        
    Returns:
        float: Deborah number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.23
    """
    return relaxation_time / observation_time


def drag_coefficient_sphere(
    reynolds_number: float
) -> float:
    """
    Calculates drag coefficient for flow around a sphere.
    
    Args:
        reynolds_number (float): Reynolds number (dimensionless)
        
    Returns:
        float: Drag coefficient (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.40
    """
    re = reynolds_number
    
    if re < 0.1:
        # Stokes flow
        cd = 24 / re
    elif re < 1000:
        # Intermediate regime
        cd = 24 / re * (1 + 0.15 * re**0.687)
    else:
        # High Reynolds number
        cd = 0.44
    
    return cd


def drag_force(
    drag_coefficient: float,
    fluid_density: float,
    velocity: float,
    reference_area: float
) -> float:
    """
    Calculates drag force on an object.
    
    Args:
        drag_coefficient (float): Drag coefficient (dimensionless)
        fluid_density (float): Fluid density (kg/m³)
        velocity (float): Relative velocity (m/s)
        reference_area (float): Reference area (m²)
        
    Returns:
        float: Drag force (N)
        
    Reference:
        Chapter 5, Formula 5.41
    """
    return 0.5 * drag_coefficient * fluid_density * velocity**2 * reference_area


def eckert_number(
    velocity: float,
    specific_heat: float,
    temperature_difference: float
) -> float:
    """
    Calculates Eckert number for compressibility effects.
    
    Args:
        velocity (float): Characteristic velocity (m/s)
        specific_heat (float): Specific heat at constant pressure (J/(kg·K))
        temperature_difference (float): Temperature difference (K)
        
    Returns:
        float: Eckert number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.44
    """
    return velocity**2 / (specific_heat * temperature_difference)


def euler_number(
    pressure_difference: float,
    fluid_density: float,
    velocity: float
) -> float:
    """
    Calculates Euler number for pressure forces.
    
    Args:
        pressure_difference (float): Pressure difference (Pa)
        fluid_density (float): Fluid density (kg/m³)
        velocity (float): Characteristic velocity (m/s)
        
    Returns:
        float: Euler number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.54
    """
    return pressure_difference / (fluid_density * velocity**2)


def fanning_friction_factor_laminar(
    reynolds_number: float
) -> float:
    """
    Calculates Fanning friction factor for laminar flow.
    
    Args:
        reynolds_number (float): Reynolds number (dimensionless)
        
    Returns:
        float: Fanning friction factor (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.55
    """
    return 16 / reynolds_number


def fanning_friction_factor_turbulent(
    reynolds_number: float,
    relative_roughness: float = 0.0
) -> float:
    """
    Calculates Fanning friction factor for turbulent flow.
    
    Args:
        reynolds_number (float): Reynolds number (dimensionless)
        relative_roughness (float, optional): Relative roughness (ε/D). Defaults to 0.0.
        
    Returns:
        float: Fanning friction factor (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.56
    """
    if relative_roughness == 0:
        # Smooth pipe
        return 0.0791 / reynolds_number**0.25
    else:
        # Rough pipe
        return 0.25 / (4 * (math.log10(relative_roughness/3.7 + 5.74/reynolds_number**0.9))**2)


def galilei_number(
    gravitational_acceleration: float,
    characteristic_length: float,
    kinematic_viscosity: float
) -> float:
    """
    Calculates Galilei number for gravitational effects.
    
    Args:
        gravitational_acceleration (float): Gravitational acceleration (m/s²)
        characteristic_length (float): Characteristic length (m)
        kinematic_viscosity (float): Kinematic viscosity (m²/s)
        
    Returns:
        float: Galilei number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.77
    """
    return gravitational_acceleration * characteristic_length**3 / kinematic_viscosity**2


def graetz_number(
    reynolds_number: float,
    prandtl_number: float,
    pipe_diameter: float,
    pipe_length: float
) -> float:
    """
    Calculates Graetz number for heat transfer analysis.
    
    Args:
        reynolds_number (float): Reynolds number (dimensionless)
        prandtl_number (float): Prandtl number (dimensionless)
        pipe_diameter (float): Pipe diameter (m)
        pipe_length (float): Pipe length (m)
        
    Returns:
        float: Graetz number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.83
    """
    return reynolds_number * prandtl_number * pipe_diameter / pipe_length


def grashof_number(
    gravitational_acceleration: float,
    thermal_expansion_coefficient: float,
    temperature_difference: float,
    characteristic_length: float,
    kinematic_viscosity: float
) -> float:
    """
    Calculates Grashof number for natural convection.
    
    Args:
        gravitational_acceleration (float): Gravitational acceleration (m/s²)
        thermal_expansion_coefficient (float): Thermal expansion coefficient (1/K)
        temperature_difference (float): Temperature difference (K)
        characteristic_length (float): Characteristic length (m)
        kinematic_viscosity (float): Kinematic viscosity (m²/s)
        
    Returns:
        float: Grashof number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.85
    """
    return (gravitational_acceleration * thermal_expansion_coefficient * 
            temperature_difference * characteristic_length**3) / kinematic_viscosity**2


def hagen_poiseuille_equation(
    pressure_drop: float,
    pipe_radius: float,
    dynamic_viscosity: float,
    pipe_length: float
) -> float:
    """
    Calculates flow rate using Hagen-Poiseuille equation for laminar flow.
    
    Args:
        pressure_drop (float): Pressure drop (Pa)
        pipe_radius (float): Pipe radius (m)
        dynamic_viscosity (float): Dynamic viscosity (Pa·s)
        pipe_length (float): Pipe length (m)
        
    Returns:
        float: Volumetric flow rate (m³/s)
        
    Reference:
        Chapter 5, Formula 5.87
    """
    return (math.pi * pipe_radius**4 * pressure_drop) / (8 * dynamic_viscosity * pipe_length)


def laplace_number(
    surface_tension: float,
    fluid_density: float,
    characteristic_length: float,
    dynamic_viscosity: float
) -> float:
    """
    Calculates Laplace number for surface tension effects.
    
    Args:
        surface_tension (float): Surface tension (N/m)
        fluid_density (float): Fluid density (kg/m³)
        characteristic_length (float): Characteristic length (m)
        dynamic_viscosity (float): Dynamic viscosity (Pa·s)
        
    Returns:
        float: Laplace number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.93
    """
    return (surface_tension * fluid_density * characteristic_length) / dynamic_viscosity**2


def lewis_number(
    thermal_diffusivity: float,
    mass_diffusivity: float
) -> float:
    """
    Calculates Lewis number for simultaneous heat and mass transfer.
    
    Args:
        thermal_diffusivity (float): Thermal diffusivity (m²/s)
        mass_diffusivity (float): Mass diffusivity (m²/s)
        
    Returns:
        float: Lewis number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.94
    """
    return thermal_diffusivity / mass_diffusivity


def mach_number(
    velocity: float,
    sound_speed: float
) -> float:
    """
    Calculates Mach number for compressible flow.
    
    Args:
        velocity (float): Flow velocity (m/s)
        sound_speed (float): Speed of sound in the medium (m/s)
        
    Returns:
        float: Mach number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.95
    """
    return velocity / sound_speed


def nusselt_number(
    heat_transfer_coefficient: float,
    characteristic_length: float,
    thermal_conductivity: float
) -> float:
    """
    Calculates Nusselt number for convective heat transfer.
    
    Args:
        heat_transfer_coefficient (float): Heat transfer coefficient (W/(m²·K))
        characteristic_length (float): Characteristic length (m)
        thermal_conductivity (float): Thermal conductivity (W/(m·K))
        
    Returns:
        float: Nusselt number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.120
    """
    return (heat_transfer_coefficient * characteristic_length) / thermal_conductivity


def ohnesorge_number(
    dynamic_viscosity: float,
    fluid_density: float,
    surface_tension: float,
    characteristic_length: float
) -> float:
    """
    Calculates Ohnesorge number for atomization and droplet formation.
    
    Args:
        dynamic_viscosity (float): Dynamic viscosity (Pa·s)
        fluid_density (float): Fluid density (kg/m³)
        surface_tension (float): Surface tension (N/m)
        characteristic_length (float): Characteristic length (m)
        
    Returns:
        float: Ohnesorge number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.121
    """
    return dynamic_viscosity / math.sqrt(fluid_density * surface_tension * characteristic_length)


def prandtl_number(
    dynamic_viscosity: float,
    specific_heat: float,
    thermal_conductivity: float
) -> float:
    """
    Calculates Prandtl number for momentum and heat transfer.
    
    Args:
        dynamic_viscosity (float): Dynamic viscosity (Pa·s)
        specific_heat (float): Specific heat at constant pressure (J/(kg·K))
        thermal_conductivity (float): Thermal conductivity (W/(m·K))
        
    Returns:
        float: Prandtl number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.123
    """
    return (dynamic_viscosity * specific_heat) / thermal_conductivity


def schmidt_number(
    kinematic_viscosity: float,
    mass_diffusivity: float
) -> float:
    """
    Calculates Schmidt number for momentum and mass transfer.
    
    Args:
        kinematic_viscosity (float): Kinematic viscosity (m²/s)
        mass_diffusivity (float): Mass diffusivity (m²/s)
        
    Returns:
        float: Schmidt number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.128
    """
    return kinematic_viscosity / mass_diffusivity


def sherwood_number(
    mass_transfer_coefficient: float,
    characteristic_length: float,
    mass_diffusivity: float
) -> float:
    """
    Calculates Sherwood number for convective mass transfer.
    
    Args:
        mass_transfer_coefficient (float): Mass transfer coefficient (m/s)
        characteristic_length (float): Characteristic length (m)
        mass_diffusivity (float): Mass diffusivity (m²/s)
        
    Returns:
        float: Sherwood number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.129
    """
    return (mass_transfer_coefficient * characteristic_length) / mass_diffusivity


def strouhal_number(
    characteristic_frequency: float,
    characteristic_length: float,
    characteristic_velocity: float
) -> float:
    """
    Calculates Strouhal number for oscillatory flow.
    
    Args:
        characteristic_frequency (float): Characteristic frequency (Hz)
        characteristic_length (float): Characteristic length (m)
        characteristic_velocity (float): Characteristic velocity (m/s)
        
    Returns:
        float: Strouhal number (dimensionless)
        
    Reference:
        Chapter 5, Formula 5.135
    """
    return (characteristic_frequency * characteristic_length) / characteristic_velocity


def torricelli_equation(
    height: float,
    gravitational_acceleration: float = 9.81
) -> float:
    """
    Calculates velocity of efflux using Torricelli's equation.
    
    Args:
        height (float): Height of fluid column (m)
        gravitational_acceleration (float, optional): Gravitational acceleration (m/s²). Defaults to 9.81.
        
    Returns:
        float: Velocity of efflux (m/s)
        
    Reference:
        Chapter 5, Formula 5.140
    """
    return math.sqrt(2 * gravitational_acceleration * height)
