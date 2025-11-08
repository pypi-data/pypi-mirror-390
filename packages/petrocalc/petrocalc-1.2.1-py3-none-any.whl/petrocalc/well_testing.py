"""
Well test analysis calculations.

This module contains functions for well test analysis including:
- Pressure buildup analysis
- Flow test analysis
- Fracture analysis
- Skin factor calculations
- Permeability estimation
- Dimensionless parameters
"""

import math
from typing import Union, Tuple, Optional


def analysis_flow_test_varying_rates(
    time1: float,
    time2: float,
    flow_rate1: float,
    flow_rate2: float,
    initial_pressure: float,
    wellbore_flowing_pressure2: float,
    wellbore_flowing_pressure1: float,
    pressure_at_1h: float,
    flow_rate: float,
    volume_factor: float,
    thickness: float,
    viscosity: float,
    porosity: float,
    compressibility: float,
    wellbore_radius: float
) -> Tuple[float, float]:
    """
    Analysis of a flow test with smoothly varying rates.
    
    Args:
        time1 (float): Time at Pwf1 from given values or trendline (h)
        time2 (float): Time at Pwf2 from given values or trendline (h)
        flow_rate1 (float): Flow rate at Pwf1 (STB/day)
        flow_rate2 (float): Flow rate at Pwf2 (STB/day)
        initial_pressure (float): Initial pressure (psi)
        wellbore_flowing_pressure2 (float): Well flowing pressure at point 2 (psi)
        wellbore_flowing_pressure1 (float): Well flowing pressure at point 1 (psi)
        pressure_at_1h (float): Pressure value at t = 1 h (psi)
        flow_rate (float): Flow rate (STB/day)
        volume_factor (float): Volume factor (RB/STB)
        thickness (float): Thickness of reservoir (ft)
        viscosity (float): Viscosity of oil (cP)
        porosity (float): Porosity (fraction)
        compressibility (float): Compressibility (1/psi)
        wellbore_radius (float): Wellbore radius (ft)
        
    Returns:
        Tuple[float, float]: Permeability (mD), skin factor (dimensionless)
        
    Reference:
        Chapter 3, Formula 3.1
    """
    # Calculate slope
    slope = (wellbore_flowing_pressure2 - wellbore_flowing_pressure1) / math.log10(time2 / time1)
    
    # Calculate permeability
    permeability = (162.6 * flow_rate * volume_factor * viscosity) / (slope * thickness)
    
    # Calculate skin factor
    skin_term = (initial_pressure - pressure_at_1h) / slope
    log_term = math.log10((permeability) / (porosity * viscosity * compressibility * wellbore_radius**2)) + 3.23
    skin_factor = 1.151 * (skin_term - log_term)
    
    return permeability, skin_factor


def post_fracture_flow_test_boundary_effects(
    gas_flow_rate: float,
    gas_formation_volume_factor: float,
    slope_curve: float,
    slope_linear: float,
    initial_adjusted_pressure: float,
    adjusted_pressure_1h: float,
    thickness: float,
    porosity: float,
    compressibility: float,
    wellbore_radius: float,
    viscosity: float,
    dimensionless_pressure: float,
    adjusted_pressure_difference_mp: float,
    adjusted_delta_time: float,
    time_end_linear_flow: float
) -> Tuple[float, float, float, float, float]:
    """
    Analysis of a post-fracture constant-rate flow test with boundary effects.
    
    Args:
        gas_flow_rate (float): Gas flow rate (MSCF/day)
        gas_formation_volume_factor (float): Gas formation volume factor (RB/MSCF)
        slope_curve (float): Slope from curve (psi/cycle)
        slope_linear (float): Slope from linear region of curve (psi/cycle)
        initial_adjusted_pressure (float): Initial adjusted well pressure (psi)
        adjusted_pressure_1h (float): Adjusted well pressure at t = 1 h (psi)
        thickness (float): Formation thickness (ft)
        porosity (float): Porosity (dimensionless)
        compressibility (float): Compressibility (1/psi)
        wellbore_radius (float): Radius of wellbore (ft)
        viscosity (float): Viscosity (cP)
        dimensionless_pressure (float): Dimensionless pressure (dimensionless)
        adjusted_pressure_difference_mp (float): Adjusted pressure difference at match point (psi)
        adjusted_delta_time (float): Adjusted delta time from derivative curve (h)
        time_end_linear_flow (float): Time of end of linear or pseudo radial flow (dimensionless)
        
    Returns:
        Tuple[float, float, float, float, float]: 
            - Permeability (mD)
            - Length of fracture for pseudo radial flow (ft)
            - Length of fracture for linear flow (ft)
            - Length of fracture from match point analysis (ft)
            - Skin factor (dimensionless)
            
    Reference:
        Lee, J., Rollins J.B., and Spivey J.P. 2003, Pressure Transient Testing, Vol. 9
    """
    # Calculate permeability
    permeability = (162.6 * gas_flow_rate * gas_formation_volume_factor * viscosity) / (slope_curve * thickness)
    
    # Length of fracture for pseudo radial flow
    log_term = math.log10((permeability) / (porosity * viscosity * compressibility * wellbore_radius**2)) + 3.23
    length_fracture_pr = 1.151 * (initial_adjusted_pressure - adjusted_pressure_1h) / slope_curve - log_term
    
    # Length of fracture for linear flow
    length_fracture_linear = 2 * wellbore_radius * (2.71 - dimensionless_pressure)
    
    # Length of fracture from match point analysis
    length_fracture_mp = (4.064 * gas_flow_rate * gas_formation_volume_factor * slope_linear) / \
                        (thickness * math.sqrt(permeability) * math.sqrt(viscosity * porosity * compressibility))
    
    # Skin factor
    skin_factor = (141.2 * gas_flow_rate * gas_formation_volume_factor * viscosity) / \
                  (permeability * thickness) - dimensionless_pressure
    
    return permeability, length_fracture_pr, length_fracture_linear, length_fracture_mp, skin_factor


def post_fracture_buildup_wellbore_storage(
    gas_flow_rate: float,
    gas_formation_volume_factor: float,
    thickness: float,
    porosity: float,
    compressibility: float,
    viscosity: float,
    permeability: float,
    dimensionless_pressure_mp: float,
    fracture_length: float,
    equivalent_adjusted_delta_time: float,
    time_end_linear_flow: float,
    dimensionless_fracture_conductivity: float,
    dimensionless_wellbore_storage: float
) -> Tuple[float, float, float, float]:
    """
    Analysis of a post-fracture pressure buildup test with wellbore-storage distortion.
    
    Args:
        gas_flow_rate (float): Gas flow rate (MSCF/day)
        gas_formation_volume_factor (float): Gas formation volume factor (RB/MSCF)
        thickness (float): Formation thickness (ft)
        porosity (float): Porosity (dimensionless)
        compressibility (float): Compressibility (1/psi)
        viscosity (float): Viscosity (cP)
        permeability (float): Permeability (mD)
        dimensionless_pressure_mp (float): Dimensionless pressure at match point (dimensionless)
        fracture_length (float): Length of fracture (ft)
        equivalent_adjusted_delta_time (float): Equivalent adjusted delta time from derivative curve (h)
        time_end_linear_flow (float): Time of end of linear or pseudo radial flow (dimensionless)
        dimensionless_fracture_conductivity (float): Dimensionless fracture conductivity (dimensionless)
        dimensionless_wellbore_storage (float): Dimensionless wellbore storage coefficient (dimensionless)
        
    Returns:
        Tuple[float, float, float, float]: 
            - Wellbore storage coefficient (bbl/psi)
            - Min fracture conductivity for infinite conductive fracture (mD·ft)
            - Length of fracture from match point analysis (ft)
            - Adjusted pressure difference at match point (psi)
            
    Reference:
        Lee, J., Rollins J.B., and Spivey J.P. 2003, Pressure Transient Testing, Vol. 9, 
        SPE Textbook Series, Chapter: 6, Page: 127.
    """
    # Wellbore storage coefficient
    wellbore_storage = (141.2 * gas_flow_rate * gas_formation_volume_factor * viscosity) / \
                      (permeability * thickness * dimensionless_pressure_mp)
    
    # Min fracture conductivity for infinite conductive fracture
    min_fracture_conductivity = (0.0002637 * permeability) / \
                               (porosity * viscosity * compressibility) * \
                               (equivalent_adjusted_delta_time / time_end_linear_flow)**0.5
    
    # Length of fracture from match point analysis
    length_fracture_mp = math.sqrt((porosity * thickness * compressibility * fracture_length**2 * dimensionless_wellbore_storage) / 0.8936)
    
    # Adjusted pressure difference at match point
    adjusted_pressure_diff_mp = (3.14 * permeability * dimensionless_fracture_conductivity) / fracture_length
    
    return wellbore_storage, min_fracture_conductivity, length_fracture_mp, adjusted_pressure_diff_mp


def analysis_well_pi_test(
    average_reservoir_pressure: float,
    flow_rate: float,
    well_flowing_pressure: float,
    volume_factor: float,
    thickness: float,
    oil_viscosity: float,
    drainage_radius: float,
    wellbore_radius: float
) -> Tuple[float, float, float]:
    """
    Analysis of a well from a PI (productivity index) test.
    
    Args:
        average_reservoir_pressure (float): Average reservoir pressure (psi)
        flow_rate (float): Flow rate (STB/day)
        well_flowing_pressure (float): Well flowing pressure (psi)
        volume_factor (float): Volume factor (RB/STB)
        thickness (float): Thickness of reservoir (ft)
        oil_viscosity (float): Oil viscosity (cP)
        drainage_radius (float): Drainage radius (ft)
        wellbore_radius (float): Wellbore radius (ft)
        
    Returns:
        Tuple[float, float, float]: 
            - Productivity index (STB/day/psi)
            - Average permeability (mD)
            - Skin factor (dimensionless)
            
    Reference:
        Chapter 3, Formula 3.4
    """
    # Productivity index
    productivity_index = flow_rate / (average_reservoir_pressure - well_flowing_pressure)
    
    # Average permeability
    permeability = (141.2 * flow_rate * volume_factor * oil_viscosity) / \
                  (thickness * (average_reservoir_pressure - well_flowing_pressure) * 
                   math.log(drainage_radius / wellbore_radius))
    
    # Skin factor (assuming zero for ideal well)
    skin_factor = 0.0  # Can be calculated if additional data is available
    
    return productivity_index, permeability, skin_factor


def diffusion_depth_geothermal(
    hydraulic_diffusivity: float,
    time: float
) -> float:
    """
    Calculates diffusion depth in a geothermal well.
    
    Args:
        hydraulic_diffusivity (float): Hydraulic diffusivity (ft²/s)
        time (float): Time (s)
        
    Returns:
        float: Diffusion depth (ft)
        
    Reference:
        Chapter 3, Formula 3.10
    """
    return math.sqrt(hydraulic_diffusivity * time)


def dimensionless_buildup_time(
    permeability: float,
    buildup_time: float,
    porosity: float,
    viscosity: float,
    compressibility: float,
    wellbore_radius: float
) -> float:
    """
    Calculates dimensionless buildup time.
    
    Args:
        permeability (float): Permeability (mD)
        buildup_time (float): Buildup time (hours)
        porosity (float): Porosity (fraction)
        viscosity (float): Viscosity (cP)
        compressibility (float): Total compressibility (1/psi)
        wellbore_radius (float): Wellbore radius (ft)
        
    Returns:
        float: Dimensionless buildup time (dimensionless)
        
    Reference:
        Chapter 3, Formula 3.14
    """
    return (0.0002637 * permeability * buildup_time) / \
           (porosity * viscosity * compressibility * wellbore_radius**2)


def dimensionless_cumulative_production_radial_flow(
    cumulative_production: float,
    porosity: float,
    thickness: float,
    total_compressibility: float,
    drainage_radius: float,
    formation_volume_factor: float
) -> float:
    """
    Calculates dimensionless cumulative production for radial flow constant-pressure production.
    
    Args:
        cumulative_production (float): Cumulative production (STB)
        porosity (float): Porosity (fraction)
        thickness (float): Formation thickness (ft)
        total_compressibility (float): Total compressibility (1/psi)
        drainage_radius (float): Drainage radius (ft)
        formation_volume_factor (float): Formation volume factor (RB/STB)
        
    Returns:
        float: Dimensionless cumulative production (dimensionless)
        
    Reference:
        Chapter 3, Formula 3.15
    """
    pore_volume = porosity * thickness * math.pi * drainage_radius**2
    return (cumulative_production * formation_volume_factor * total_compressibility) / pore_volume


def dimensionless_drawdown_correlating_parameter_carter(
    permeability: float,
    thickness: float,
    production_time: float,
    porosity: float,
    viscosity: float,
    total_compressibility: float,
    drainage_area: float
) -> float:
    """
    Calculates dimensionless drawdown correlating parameter by Carter.
    
    Args:
        permeability (float): Permeability (mD)
        thickness (float): Formation thickness (ft)
        production_time (float): Production time (hours)
        porosity (float): Porosity (fraction)
        viscosity (float): Viscosity (cP)
        total_compressibility (float): Total compressibility (1/psi)
        drainage_area (float): Drainage area (ft²)
        
    Returns:
        float: Dimensionless drawdown correlating parameter (dimensionless)
        
    Reference:
        Chapter 3, Formula 3.16
    """
    return (0.0002637 * permeability * thickness * production_time) / \
           (porosity * viscosity * total_compressibility * drainage_area)


def dimensionless_length_linear_flow_fractured_wells(
    fracture_half_length: float,
    permeability: float,
    time: float,
    porosity: float,
    viscosity: float,
    total_compressibility: float
) -> float:
    """
    Calculates dimensionless length for linear flow constant rate production in hydraulically fractured wells.
    
    Args:
        fracture_half_length (float): Fracture half-length (ft)
        permeability (float): Permeability (mD)
        time (float): Time (hours)
        porosity (float): Porosity (fraction)
        viscosity (float): Viscosity (cP)
        total_compressibility (float): Total compressibility (1/psi)
        
    Returns:
        float: Dimensionless length (dimensionless)
        
    Reference:
        Chapter 3, Formula 3.17
    """
    return fracture_half_length / math.sqrt((0.0002637 * permeability * time) / 
                                           (porosity * viscosity * total_compressibility))


def dimensionless_pressure_linear_flow_general(
    flow_rate: float,
    formation_volume_factor: float,
    viscosity: float,
    fracture_width: float,
    pressure_initial: float,
    pressure_current: float
) -> float:
    """
    Calculates dimensionless pressure for linear flow constant rate production (general case).
    
    Args:
        flow_rate (float): Flow rate (STB/day)
        formation_volume_factor (float): Formation volume factor (RB/STB)
        viscosity (float): Viscosity (cP)
        fracture_width (float): Fracture width (ft)
        pressure_initial (float): Initial pressure (psi)
        pressure_current (float): Current pressure (psi)
        
    Returns:
        float: Dimensionless pressure (dimensionless)
        
    Reference:
        Chapter 3, Formula 3.19
    """
    return (fracture_width * (pressure_initial - pressure_current)) / \
           (flow_rate * formation_volume_factor * viscosity)


def dimensionless_pressure_radial_flow_constant_rate(
    permeability: float,
    thickness: float,
    pressure_initial: float,
    pressure_current: float,
    flow_rate: float,
    formation_volume_factor: float,
    viscosity: float
) -> float:
    """
    Calculates dimensionless pressure for radial flow constant rate production.
    
    Args:
        permeability (float): Permeability (mD)
        thickness (float): Formation thickness (ft)
        pressure_initial (float): Initial pressure (psi)
        pressure_current (float): Current pressure (psi)
        flow_rate (float): Flow rate (STB/day)
        formation_volume_factor (float): Formation volume factor (RB/STB)
        viscosity (float): Viscosity (cP)
        
    Returns:
        float: Dimensionless pressure (dimensionless)
        
    Reference:
        Chapter 3, Formula 3.22
    """
    return (2 * math.pi * permeability * thickness * (pressure_initial - pressure_current)) / \
           (141.2 * flow_rate * formation_volume_factor * viscosity)


def radius_of_investigation_flow_time(
    permeability: float,
    flow_time: float,
    porosity: float,
    viscosity: float,
    total_compressibility: float
) -> float:
    """
    Calculates radius of investigation during flow time.
    
    Args:
        permeability (float): Permeability (mD)
        flow_time (float): Flow time (hours)
        porosity (float): Porosity (fraction)
        viscosity (float): Viscosity (cP)
        total_compressibility (float): Total compressibility (1/psi)
        
    Returns:
        float: Radius of investigation (ft)
        
    Reference:
        Chapter 3, Formula 3.47
    """
    return math.sqrt((0.0002637 * permeability * flow_time) / 
                     (porosity * viscosity * total_compressibility))


def radius_of_investigation_shutin_time(
    permeability: float,
    shutin_time: float,
    porosity: float,
    viscosity: float,
    total_compressibility: float
) -> float:
    """
    Calculates radius of investigation during shut-in time.
    
    Args:
        permeability (float): Permeability (mD)
        shutin_time (float): Shut-in time (hours)
        porosity (float): Porosity (fraction)
        viscosity (float): Viscosity (cP)
        total_compressibility (float): Total compressibility (1/psi)
        
    Returns:
        float: Radius of investigation (ft)
        
    Reference:
        Chapter 3, Formula 3.48
    """
    return math.sqrt((0.0002637 * permeability * shutin_time) / 
                     (porosity * viscosity * total_compressibility))


def raymer_hunt_transform_porosity_transit_time(
    delta_t_matrix: float,
    delta_t_fluid: float,
    delta_t_log: float
) -> float:
    """
    Calculates porosity from transit time using Raymer-Hunt transform.
    
    Args:
        delta_t_matrix (float): Matrix transit time (μs/ft)
        delta_t_fluid (float): Fluid transit time (μs/ft)
        delta_t_log (float): Log reading transit time (μs/ft)
        
    Returns:
        float: Porosity (fraction)
        
    Reference:
        Chapter 3, Formula 3.49
    """
    return (delta_t_log - delta_t_matrix) / (delta_t_fluid - delta_t_matrix)


def reservoir_permeability_well_test(
    flow_rate: float,
    formation_volume_factor: float,
    viscosity: float,
    thickness: float,
    slope: float
) -> float:
    """
    Calculates reservoir permeability from well test data.
    
    Args:
        flow_rate (float): Flow rate (STB/day)
        formation_volume_factor (float): Formation volume factor (RB/STB)
        viscosity (float): Viscosity (cP)
        thickness (float): Formation thickness (ft)
        slope (float): Slope from pressure buildup plot (psi/cycle)
        
    Returns:
        float: Reservoir permeability (mD)
        
    Reference:
        Chapter 3, Formula 3.50
    """
    return (162.6 * flow_rate * formation_volume_factor * viscosity) / (slope * thickness)


def shutin_time_buildup_test_dietz(
    porosity: float,
    viscosity: float,
    total_compressibility: float,
    drainage_area: float,
    permeability: float,
    shape_factor: float = 31.6
) -> float:
    """
    Calculates shut-in time for pressure build-up test using Dietz method.
    
    Args:
        porosity (float): Porosity (fraction)
        viscosity (float): Viscosity (cP)
        total_compressibility (float): Total compressibility (1/psi)
        drainage_area (float): Drainage area (ft²)
        permeability (float): Permeability (mD)
        shape_factor (float, optional): Shape factor for drainage area. Defaults to 31.6 (circle).
        
    Returns:
        float: Required shut-in time (hours)
        
    Reference:
        Chapter 3, Formula 3.51
    """
    return (porosity * viscosity * total_compressibility * drainage_area) / \
           (0.0002637 * permeability * shape_factor)


def skin_infinite_acting_pseudoradial_flow(
    flow_rate: float,
    formation_volume_factor: float,
    viscosity: float,
    permeability: float,
    thickness: float,
    pressure_1h: float,
    initial_pressure: float,
    porosity: float,
    total_compressibility: float,
    wellbore_radius: float
) -> float:
    """
    Calculates skin factor during infinite-acting pseudoradial flow for vertical wells.
    
    Args:
        flow_rate (float): Flow rate (STB/day)
        formation_volume_factor (float): Formation volume factor (RB/STB)
        viscosity (float): Viscosity (cP)
        permeability (float): Permeability (mD)
        thickness (float): Formation thickness (ft)
        pressure_1h (float): Pressure at t = 1 hour (psi)
        initial_pressure (float): Initial pressure (psi)
        porosity (float): Porosity (fraction)
        total_compressibility (float): Total compressibility (1/psi)
        wellbore_radius (float): Wellbore radius (ft)
        
    Returns:
        float: Skin factor (dimensionless)
        
    Reference:
        Chapter 3, Formula 3.52
    """
    term1 = (initial_pressure - pressure_1h) * permeability * thickness
    term2 = 141.2 * flow_rate * formation_volume_factor * viscosity
    term3 = math.log10(permeability / (porosity * viscosity * total_compressibility * wellbore_radius**2))
    
    return 1.151 * (term1 / term2 - term3 - 3.23)
