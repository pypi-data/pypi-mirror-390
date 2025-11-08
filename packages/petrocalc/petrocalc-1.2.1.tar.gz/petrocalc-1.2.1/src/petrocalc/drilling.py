"""
Drilling and wellbore engineering calculations.

This module contains functions for drilling-related calculations including:
- Mud properties and hydraulics
- Hole cleaning and cuttings transport
- Torque and drag calculations
- Pressure losses in drilling systems
- Wellbore stability
"""

import math
from typing import Union, Tuple, Optional


def mud_weight_to_pressure_gradient(mud_weight: float, unit: str = "ppg") -> float:
    """
    Converts mud weight to pressure gradient.
    
    Args:
        mud_weight (float): Mud weight value
        unit (str): Unit of mud weight ("ppg" for pounds per gallon, "sg" for specific gravity)
        
    Returns:
        float: Pressure gradient in psi/ft
        
    Raises:
        ValueError: If unit is not supported
    """
    if unit.lower() == "ppg":
        return mud_weight * 0.052
    elif unit.lower() == "sg":
        return mud_weight * 0.433
    else:
        raise ValueError("Unit must be 'ppg' or 'sg'")


def hydrostatic_pressure(mud_weight: float, depth: float, unit: str = "ppg") -> float:
    """
    Calculates hydrostatic pressure at a given depth.
    
    Args:
        mud_weight (float): Mud weight in ppg or specific gravity
        depth (float): Depth in feet
        unit (str): Unit of mud weight ("ppg" or "sg")
        
    Returns:
        float: Hydrostatic pressure in psi
    """
    pressure_gradient = mud_weight_to_pressure_gradient(mud_weight, unit)
    return pressure_gradient * depth


def annular_velocity(flow_rate: float, hole_diameter: float, pipe_diameter: float) -> float:
    """
    Calculates annular velocity in drilling operations.
    
    Args:
        flow_rate (float): Flow rate in gpm
        hole_diameter (float): Hole diameter in inches
        pipe_diameter (float): Pipe outer diameter in inches
        
    Returns:
        float: Annular velocity in ft/min
    """
    annular_area = (hole_diameter**2 - pipe_diameter**2) * math.pi / 4
    return (flow_rate * 0.3208) / (annular_area / 144)


def pipe_velocity(flow_rate: float, pipe_inner_diameter: float) -> float:
    """
    Calculates velocity inside pipe.
    
    Args:
        flow_rate (float): Flow rate in gpm
        pipe_inner_diameter (float): Pipe inner diameter in inches
        
    Returns:
        float: Pipe velocity in ft/min
    """
    pipe_area = (pipe_inner_diameter**2 * math.pi) / 4
    return (flow_rate * 0.3208) / (pipe_area / 144)


def reynolds_number(velocity: float, diameter: float, density: float, viscosity: float) -> float:
    """
    Calculates Reynolds number for flow in pipes.
    
    Args:
        velocity (float): Velocity in ft/sec
        diameter (float): Pipe diameter in ft
        density (float): Fluid density in lb/ft³
        viscosity (float): Dynamic viscosity in cp
        
    Returns:
        float: Reynolds number (dimensionless)
    """
    return (density * velocity * diameter) / (viscosity * 6.72e-4)


def fanning_friction_factor(reynolds_number: float, roughness: float = 0.0006) -> float:
    """
    Calculates Fanning friction factor using Colebrook-White equation.
    
    Args:
        reynolds_number (float): Reynolds number
        roughness (float): Relative roughness (dimensionless)
        
    Returns:
        float: Fanning friction factor
    """
    if reynolds_number < 2100:
        return 16 / reynolds_number
    else:
        # Simplified approximation for turbulent flow
        return 0.0791 / (reynolds_number**0.25)


def pressure_loss_in_pipe(
    flow_rate: float, 
    pipe_length: float, 
    pipe_diameter: float, 
    density: float, 
    viscosity: float
) -> float:
    """
    Calculates pressure loss in pipe due to friction.
    
    Args:
        flow_rate (float): Flow rate in gpm
        pipe_length (float): Pipe length in ft
        pipe_diameter (float): Pipe inner diameter in inches
        density (float): Fluid density in lb/ft³
        viscosity (float): Dynamic viscosity in cp
        
    Returns:
        float: Pressure loss in psi
    """
    velocity = pipe_velocity(flow_rate, pipe_diameter)
    velocity_fps = velocity / 60  # Convert to ft/sec
    diameter_ft = pipe_diameter / 12  # Convert to ft
    
    re = reynolds_number(velocity_fps, diameter_ft, density, viscosity)
    f = fanning_friction_factor(re)
    
    return (2 * f * density * velocity_fps**2 * pipe_length) / (32.174 * diameter_ft * 144)


def critical_flow_rate(
    hole_diameter: float, 
    pipe_diameter: float, 
    cutting_diameter: float,
    fluid_density: float,
    cutting_density: float
) -> float:
    """
    Calculates critical flow rate for hole cleaning.
    
    Args:
        hole_diameter (float): Hole diameter in inches
        pipe_diameter (float): Pipe outer diameter in inches
        cutting_diameter (float): Cutting particle diameter in inches
        fluid_density (float): Drilling fluid density in ppg
        cutting_density (float): Cutting density in ppg
        
    Returns:
        float: Critical flow rate in gpm
    """
    # Simplified Moore's equation
    annular_area = (hole_diameter**2 - pipe_diameter**2) * math.pi / 4
    
    # Terminal settling velocity
    terminal_velocity = 116.6 * math.sqrt(
        (cutting_density - fluid_density) * cutting_diameter / fluid_density
    )
    
    # Critical flow rate
    return (terminal_velocity * annular_area) / (0.3208 * 144)


def torque_calculation(
    weight_on_bit: float,
    bit_diameter: float,
    formation_strength: float,
    friction_coefficient: float = 0.35
) -> float:
    """
    Calculates drilling torque at the bit.
    
    Args:
        weight_on_bit (float): Weight on bit in lbs
        bit_diameter (float): Bit diameter in inches
        formation_strength (float): Formation compressive strength in psi
        friction_coefficient (float): Friction coefficient between bit and rock
        
    Returns:
        float: Torque in ft-lbs
    """
    bit_radius = bit_diameter / 24  # Convert to ft and get radius
    torque = friction_coefficient * weight_on_bit * bit_radius
    return torque


def hookload_calculation(
    pipe_weight: float,
    buoyancy_factor: float,
    overpull: float = 0
) -> float:
    """
    Calculates hookload during drilling operations.
    
    Args:
        pipe_weight (float): Total pipe weight in air in lbs
        buoyancy_factor (float): Buoyancy factor (dimensionless)
        overpull (float): Additional overpull in lbs
        
    Returns:
        float: Hookload in lbs
    """
    return pipe_weight * buoyancy_factor + overpull


def buoyancy_factor(mud_density: float, steel_density: float = 65.4) -> float:
    """
    Calculates buoyancy factor for steel in drilling mud.
    
    Args:
        mud_density (float): Mud density in lb/ft³
        steel_density (float): Steel density in lb/ft³ (default 65.4)
        
    Returns:
        float: Buoyancy factor (dimensionless)
    """
    return 1 - (mud_density / steel_density)


def accumulator_capacity(
    bottle_volume_per_capacity: float,
    precharge_pressure: float,
    system_pressure: float,
    final_pressure: float
) -> float:
    """
    Calculates accumulator capacity for drilling operations.
    
    Args:
        bottle_volume_per_capacity (float): Bottle volume per capacity (gallons)
        precharge_pressure (float): Pre-charge pressure (psi)
        system_pressure (float): System pressure (psi)
        final_pressure (float): Final pressure (psi)
        
    Returns:
        float: Accumulator capacity (gallon)
        
    Reference:
        Lapeyrouse, N. J., 2002, Formulas and Calculations for Drilling, 
        Production and Workover, Second Edition, Gulf Professional Publishing, Page: 39.
    """
    return bottle_volume_per_capacity * ((precharge_pressure - final_pressure) / 
                                        (precharge_pressure - system_pressure))


def accumulator_capacity(
    pump_volume: float,
    operating_time: float,
    safety_factor: float = 1.5
) -> float:
    """
    Calculates required accumulator capacity for drilling operations.
    
    Args:
        pump_volume (float): Pump volume per stroke (bbl)
        operating_time (float): Required operating time without pumps (minutes)
        safety_factor (float, optional): Safety factor. Defaults to 1.5.
        
    Returns:
        float: Required accumulator capacity (gallons)
        
    Reference:
        Standard drilling engineering calculations
    """
    return pump_volume * operating_time * safety_factor * 42  # Convert bbl to gallons


def accumulator_precharge_pressure(
    total_accumulator_volume: float,
    starting_pressure: float,
    volume_fluid_removed: float,
    final_pressure: float
) -> float:
    """
    Calculates accumulator precharge pressure.
    
    Args:
        total_accumulator_volume (float): Total accumulator volume (bbl)
        starting_pressure (float): Starting accumulator pressure (psi)
        volume_fluid_removed (float): Volume of fluid removed (bbl)
        final_pressure (float): Final accumulator pressure (psi)
        
    Returns:
        float: Accumulator pressure (psi)
        
    Reference:
        Lapeyrouse, N. J., 2002, Formulas and Calculations for Drilling, 
        Production and Workover, Second Edition, Gulf Professional Publishing, Page: 41.
    """
    return ((volume_fluid_removed / total_accumulator_volume) * 
            (final_pressure - starting_pressure)) / (starting_pressure - final_pressure)


def accumulator_precharge_pressure(
    operating_pressure: float,
    pressure_ratio: float = 0.6
) -> float:
    """
    Calculates accumulator precharge pressure.
    
    Args:
        operating_pressure (float): Operating pressure (psi)
        pressure_ratio (float, optional): Precharge pressure ratio. Defaults to 0.6.
        
    Returns:
        float: Precharge pressure (psi)
        
    Reference:
        Standard drilling engineering calculations
    """
    return operating_pressure * pressure_ratio


def amount_additive_cement_slurry_density(
    required_density: float,
    cement_specific_gravity: float,
    cement_water_requirement: float,
    additive_water_requirement: float,
    additive_specific_gravity: float
) -> float:
    """
    Calculates amount of additive required to achieve a required cement slurry density.
    
    Args:
        required_density (float): Required slurry density (lb/gal)
        cement_specific_gravity (float): Specific gravity of cement (unitless)
        cement_water_requirement (float): Water requirement of cement (gal/stroke)
        additive_water_requirement (float): Water requirement of additive (gal/stroke)
        additive_specific_gravity (float): Specific gravity of additive (unitless)
        
    Returns:
        float: Amount of additive required (lb/stroke)
        
    Reference:
        Lapeyrouse, N. J., 2002, Formulas and Calculations for Drilling, 
        Production and Workover, Second Edition, Gulf Professional Publishing, Page: 53.
    """
    numerator = ((required_density * 11.207983 / cement_specific_gravity) + 
                (required_density * cement_water_requirement) - 94 - 
                (8.33 * cement_water_requirement))
    
    denominator = ((1 + additive_water_requirement/100) - 
                  (required_density / (8.33 * additive_specific_gravity)) - 
                  (required_density * additive_water_requirement / 100))
    
    return numerator / denominator


def cement_additive_for_density(
    base_slurry_density: float,
    target_density: float,
    additive_density: float,
    slurry_volume: float
) -> float:
    """
    Calculates amount of additive required to achieve required cement slurry density.
    
    Args:
        base_slurry_density (float): Base slurry density (ppg)
        target_density (float): Target slurry density (ppg)
        additive_density (float): Additive density (ppg)
        slurry_volume (float): Slurry volume (bbl)
        
    Returns:
        float: Amount of additive required (lbs)
        
    Reference:
        Lapeyrouse, N.J., 2002, Formulas and Calculations for Drilling, 
        Production and Workover, Second Edition, Gulf Professional Publishing
    """
    density_difference = target_density - base_slurry_density
    weight_factor = density_difference / (additive_density - target_density)
    return weight_factor * slurry_volume * target_density * 350  # Convert to lbs


def amount_cement_left_in_casing(
    casing_length: float,
    setting_depth: float,
    casing_capacity: float
) -> float:
    """
    Calculates amount of cement to be left in casing.
    
    Args:
        casing_length (float): Casing length (ft)
        setting_depth (float): Setting depth of cementing tool (ft)
        casing_capacity (float): Casing capacity (ft³/ft)
        
    Returns:
        float: Amount of cement (ft³)
        
    Reference:
        Lapeyrouse, N. J., 2002, Formulas and Calculations for Drilling, 
        Production and Workover, Second Edition, Gulf Professional Publishing, Page: 58.
    """
    return (casing_length - setting_depth) * casing_capacity


def cement_left_in_casing(
    casing_capacity: float,
    displacement_volume: float
) -> float:
    """
    Calculates amount of cement to be left in casing.
    
    Args:
        casing_capacity (float): Casing capacity (bbl/ft)
        displacement_volume (float): Displacement volume (bbl)
        
    Returns:
        float: Length of cement left in casing (ft)
        
    Reference:
        Lapeyrouse, N.J., 2002, Formulas and Calculations for Drilling, 
        Production and Workover, Second Edition, Gulf Professional Publishing
    """
    return displacement_volume / casing_capacity


def amount_mud_displace_cement_drillpipe(
    drillpipe_length: float,
    drillpipe_capacity: float
) -> float:
    """
    Calculates amount of mud required to displace cement in drillpipe.
    
    Args:
        drillpipe_length (float): Length of drillpipe (ft)
        drillpipe_capacity (float): Drill pipe capacity (bbl/ft)
        
    Returns:
        float: Amount of mud required (bbl)
        
    Reference:
        Lapeyrouse, N. J., 2002, Formulas and Calculations for Drilling, 
        Production and Workover, Second Edition, Gulf Professional Publishing, Page: 58.
    """
    return drillpipe_length * drillpipe_capacity


def angle_of_twist_rod_torque(
    outer_diameter: float,
    inner_diameter: float,
    torque: float,
    length: float,
    modulus_elasticity: float,
    poisson_ratio: float
) -> Tuple[float, float, float]:
    """
    Calculates angle of twist for rod subjected to torque.
    
    Args:
        outer_diameter (float): Outer diameter (ft)
        inner_diameter (float): Inner diameter (ft)
        torque (float): Torque (ft·lbf)
        length (float): Length of section (ft)
        modulus_elasticity (float): Modulus of elasticity (psi)
        poisson_ratio (float): Poisson's ratio (dimensionless)
        
    Returns:
        Tuple[float, float, float]: Modulus of rigidity (psi), polar moment of inertia (ft⁴), angle of twist (rad)
        
    Reference:
        Samuel. E Robello. 501 Solved Problems and Calculations for Drilling Operations. 
        Sigma Quadrant. 2015. Houston, Texas, Page: 369.
    """
    # Modulus of rigidity
    modulus_rigidity = modulus_elasticity / (2 * (1 + poisson_ratio))
    
    # Polar moment of inertia
    polar_moment = (3.142 * (outer_diameter**4 - inner_diameter**4)) / 32
    
    # Angle of twist
    angle_twist = (torque * length) / (modulus_rigidity * polar_moment)
    
    return modulus_rigidity, polar_moment, angle_twist


def angle_of_twist_rod(
    elastic_modulus: float,
    poisson_ratio: float,
    outer_diameter: float,
    inner_diameter: float,
    torque: float,
    length: float
) -> float:
    """
    Calculates angle of twist for rod subjected to torque.
    
    Args:
        elastic_modulus (float): Modulus of elasticity (psi)
        poisson_ratio (float): Poisson's ratio (dimensionless)
        outer_diameter (float): Outer diameter (ft)
        inner_diameter (float): Inner diameter (ft)
        torque (float): Applied torque (ft·lbf)
        length (float): Length of section (ft)
        
    Returns:
        float: Angle of twist (radians)
        
    Reference:
        Samuel. E Robello. 501 Solved Problems and Calculations for Drilling Operations. 
        Sigma Quadrant. 2015. Houston, Texas, Page: 369.
    """
    # Modulus of rigidity
    rigidity_modulus = elastic_modulus / (2 * (1 + poisson_ratio))
    
    # Polar moment of inertia
    polar_moment = (math.pi * (outer_diameter**4 - inner_diameter**4)) / 32
    
    # Angle of twist
    return (torque * length) / (rigidity_modulus * polar_moment)


def annular_capacity_multiple_tubing_strings(
    casing_inner_diameter: float,
    tubing1_diameter: float,
    tubing2_diameter: float
) -> float:
    """
    Calculates annular capacity between casing and multiple strings of tubing.
    
    Args:
        casing_inner_diameter (float): Inner diameter of casing (in.)
        tubing1_diameter (float): Diameter of tubing 1 (in.)
        tubing2_diameter (float): Diameter of tubing 2 (in.)
        
    Returns:
        float: Annular capacity (gal/ft)
        
    Reference:
        Lyons, W. C., Carter, T., and Lapeyrouse, N. J., 2012, Formulas and Calculations 
        for Drilling, Production and Workover, Third Edition, Gulf Professional Publishing, Page: 15.
    """
    return (casing_inner_diameter**2 - tubing1_diameter**2 - tubing2_diameter**2) / 1029.4


def annular_capacity_multiple_tubing(
    casing_inner_diameter: float,
    tubing_diameters: list
) -> float:
    """
    Calculates annular capacity between casing and multiple strings of tubing.
    
    Args:
        casing_inner_diameter (float): Inner diameter of casing (in.)
        tubing_diameters (list): List of tubing diameters (in.)
        
    Returns:
        float: Annular capacity (gal/ft)
        
    Reference:
        Lyons, W. C., Carter, T., and Lapeyrouse, N. J., 2012, Formulas and Calculations 
        for Drilling, Production and Workover, Third Edition, Gulf Professional Publishing, Page: 15.
    """
    tubing_area_sum = sum(d**2 for d in tubing_diameters)
    return (casing_inner_diameter**2 - tubing_area_sum) / 1029.4


def annular_velocity_gpm(
    circulation_rate: float,
    hole_diameter: float,
    pipe_diameter: float
) -> float:
    """
    Calculates annular velocity using circulation rate in GPM.
    
    Args:
        circulation_rate (float): Circulation rate (gpm)
        hole_diameter (float): Inside diameter of casing or hole size (in.)
        pipe_diameter (float): Outside diameter of pipe, tubing or collars (in.)
        
    Returns:
        float: Annular velocity (ft/min)
        
    Reference:
        Lapeyrouse, N. J., 2002, Formulas and Calculations for Drilling, 
        Production and Workover, Second Edition, Gulf Professional Publishing, Page: 10.
    """
    return (24.5 * circulation_rate) / (hole_diameter**2 - pipe_diameter**2)


def annular_velocity_bbl_min(
    pump_output: float,
    hole_diameter: float,
    pipe_diameter: float
) -> float:
    """
    Calculates annular velocity using pump output in bbl/min.
    
    Args:
        pump_output (float): Pump output (bbl/min)
        hole_diameter (float): Inside diameter of casing or hole size (in.)
        pipe_diameter (float): Outside diameter of pipe, tubing or collars (in.)
        
    Returns:
        float: Annular velocity (ft/min)
        
    Reference:
        Lyons, W. C., Carter, T., and Lapeyrouse, N. J., 2012, Formulas and Calculations 
        for Drilling, Production and Workover, Third Edition, Gulf Professional Publishing, Page: 10.
    """
    return (pump_output * 1029.4) / (hole_diameter**2 - pipe_diameter**2)


def annular_volume_capacity(
    casing_inner_diameter: float,
    pipe_outer_diameter: float,
    length: float
) -> float:
    """
    Calculates annular volume capacity of pipe.
    
    Args:
        casing_inner_diameter (float): Inner diameter of casing against pipe (in.)
        pipe_outer_diameter (float): Outside diameter of pipe (in.)
        length (float): Length of pipe (ft)
        
    Returns:
        float: Annular volume capacity (bbl)
        
    Reference:
        Samuel. E Robello. 501 Solved Problems and Calculations for Drilling Operations. 
        Sigma Quadrant. 2015. Houston, Texas, Page: 44.
    """
    return (0.7854 * (casing_inner_diameter**2 - pipe_outer_diameter**2) * length) / 808.5


def api_water_loss_30min(
    water_loss_7_5_min: float,
    spurt_loss: float
) -> float:
    """
    Calculates API water loss for 30 minutes from 7.5 minute test.
    
    Args:
        water_loss_7_5_min (float): Water loss in 7.5 minutes (cm³)
        spurt_loss (float): Spurt loss (cm³)
        
    Returns:
        float: Water loss in 30 minutes (cm³)
        
    Reference:
        Samuel. E Robello. 501 Solved Problems and Calculations for Drilling Operations. 
        Sigma Quadrant. 2015. Houston, Texas, Page: 199.
    """
    return (2 * water_loss_7_5_min) - spurt_loss


def area_below_casing_shoe(
    casing_diameter: float
) -> float:
    """
    Calculates area below the casing shoe.
    
    Args:
        casing_diameter (float): Casing diameter (in.)
        
    Returns:
        float: Area below shoe (in.²)
        
    Reference:
        Lapeyrouse, N. J., 2002, Formulas and Calculations for Drilling, 
        Production and Workover, Second Edition, Gulf Professional Publishing, Page: 67.
    """
    return casing_diameter**2 * 0.7854


def axial_loads_in_slips(
    pipe_cross_section: float,
    yield_strength: float,
    outside_radius: float,
    slip_length: float,
    transverse_load_factor: float
) -> tuple:
    """
    Calculates axial loads in slips.
    
    Args:
        pipe_cross_section (float): Cross sectional area of the pipe body (in.²)
        yield_strength (float): Yield strength of the casing (psi)
        outside_radius (float): Outside casing radius (in.)
        slip_length (float): Slip gripping length (in.)
        transverse_load_factor (float): Transverse load factor (dimensionless)
        
    Returns:
        tuple: (critical_axial_load (lbf), crushing_factor (dimensionless))
        
    Reference:
        Suman Jr, G. O., & Ellis, R. C. (1977). Cementing Handbook. World Oil, Page: 18.
    """
    # Crushing factor
    term1 = (outside_radius * transverse_load_factor) / slip_length
    term2 = ((outside_radius * transverse_load_factor) / slip_length)**2
    crushing_factor = 1 / (1 + term1 + math.sqrt(term2))
    
    # Critical axial load
    critical_load = crushing_factor * pipe_cross_section * yield_strength
    
    return critical_load, crushing_factor


def bit_nozzle_pressure_loss(
    flow_rate: float,
    mud_weight: float,
    nozzle_area: float
) -> float:
    """
    Calculates bit nozzle pressure loss.
    
    Args:
        flow_rate (float): Flow rate (gpm)
        mud_weight (float): Mud weight (ppg)
        nozzle_area (float): Total nozzle area (in.²)
        
    Returns:
        float: Bit nozzle pressure loss (psi)
        
    Reference:
        Lapeyrouse, N. J., 2002, Formulas and Calculations for Drilling, 
        Production and Workover, Second Edition, Gulf Professional Publishing, Page: 165.
    """
    return (flow_rate**2 * mud_weight) / (10858 * nozzle_area**2)


def equivalent_circulating_density(
    mud_weight: float,
    annular_pressure_loss: float,
    true_vertical_depth: float
) -> float:
    """
    Calculates equivalent circulating density (ECD).
    
    Args:
        mud_weight (float): Static mud weight (ppg)
        annular_pressure_loss (float): Annular pressure loss (psi)
        true_vertical_depth (float): True vertical depth (ft)
        
    Returns:
        float: Equivalent circulating density (ppg)
        
    Reference:
        Standard drilling engineering calculations
    """
    pressure_gradient_increase = annular_pressure_loss / true_vertical_depth
    return mud_weight + (pressure_gradient_increase / 0.052)


def cutting_slip_velocity(
    cutting_diameter: float,
    cutting_density: float,
    fluid_density: float,
    fluid_viscosity: float
) -> float:
    """
    Calculates cutting slip velocity in drilling fluid.
    
    Args:
        cutting_diameter (float): Cutting diameter (in.)
        cutting_density (float): Cutting density (ppg)
        fluid_density (float): Drilling fluid density (ppg)
        fluid_viscosity (float): Fluid viscosity (cP)
        
    Returns:
        float: Cutting slip velocity (ft/min)
        
    Reference:
        Moore's Law for cutting transport
    """
    gravity_term = (cutting_density - fluid_density) / fluid_density
    diameter_term = cutting_diameter / 12  # Convert to feet
    
    return 116.6 * math.sqrt(gravity_term * diameter_term) * (8.5 / fluid_viscosity)**0.1


def cuttings_volume_per_foot(
    hole_diameter: float
) -> float:
    """
    Calculates volume of cuttings produced per foot of hole drilled.
    
    Args:
        hole_diameter (float): Hole diameter (in.)
        
    Returns:
        float: Cuttings volume (bbl/ft)
        
    Reference:
        Standard drilling calculations
    """
    hole_area = (hole_diameter**2 * math.pi) / 4  # in.²
    return hole_area / 9702  # Convert to bbl/ft


def d_exponent(
    drilling_rate: float,
    rotary_speed: float,
    weight_on_bit: float,
    bit_diameter: float,
    mud_weight: float,
    normal_pressure_gradient: float = 0.465
) -> float:
    """
    Calculates D-exponent for pore pressure evaluation.
    
    Args:
        drilling_rate (float): Rate of penetration (ft/hr)
        rotary_speed (float): Rotary speed (rpm)
        weight_on_bit (float): Weight on bit (lbs)
        bit_diameter (float): Bit diameter (in.)
        mud_weight (float): Mud weight (ppg)
        normal_pressure_gradient (float, optional): Normal pressure gradient (psi/ft). Defaults to 0.465.
        
    Returns:
        float: D-exponent (dimensionless)
        
    Reference:
        Formation pressure evaluation techniques
    """
    normalized_rate = drilling_rate / (rotary_speed * (weight_on_bit / bit_diameter))
    mud_gradient = mud_weight * 0.052
    
    return math.log10(normalized_rate) * (normal_pressure_gradient / mud_gradient)
