"""
Petrophysics and well log analysis calculations.

This module contains functions for comprehensive well log analysis, geophysics, 
and petrophysical calculations including:
- Acoustic and sonic log calculations
- Resistivity log interpretations
- Nuclear log interpretations (neutron, density, gamma ray)
- Formation evaluation
- Seismic and geophysical calculations
- Archie's equation variations
- Wettability and formation factor calculations

Reference: Based on "Formulas and Calculations for Petroleum Engineering"
          Chapter 6: Well log analysis, geophysics, petrophysics formulas
"""

import math
from typing import Union, Tuple, Optional


# =============================================================================
# ACOUSTIC AND SONIC LOG CALCULATIONS
# =============================================================================

def acoustic_transit_time(velocity: float) -> float:
    """
    Calculate acoustic transit time from velocity.
    
    Args:
        velocity (float): Velocity in ft/s
        
    Returns:
        float: Acoustic transit time in μs/ft
        
    Reference: Bassiouni, Z., 1994, Theory, Measurement, and Interpretation 
               of Well Logs. SPE Textbook Series Vol. 4. Chapter 3, Page: 45.
    """
    if velocity <= 0:
        raise ValueError("Velocity must be positive")
    
    dt = 1e6 / velocity
    return dt


def amplitude_transmission_coefficient(
    acoustic_impedance_1: float, 
    acoustic_impedance_2: float
) -> float:
    """
    Calculate amplitude transmission coefficient in seismic reflection and refraction.
    
    Args:
        acoustic_impedance_1 (float): Acoustic impedance of layer 1 in kg/m²·s
        acoustic_impedance_2 (float): Acoustic impedance of layer 2 in kg/m²·s
        
    Returns:
        float: Amplitude transmission coefficient (dimensionless)
    """
    z1 = acoustic_impedance_1
    z2 = acoustic_impedance_2
    
    if z1 + z2 == 0:
        raise ValueError("Sum of acoustic impedances cannot be zero")
    
    t = (2 * z1) / (z2 + z1)
    return t


def apparent_resistivity(
    measured_voltage: float,
    current: float,
    geometric_factor: float
) -> float:
    """
    Calculates apparent resistivity from well log measurements.
    
    Args:
        measured_voltage (float): Measured voltage (V)
        current (float): Current (A)
        geometric_factor (float): Geometric factor (m)
        
    Returns:
        float: Apparent resistivity (ohm-m)
        
    Reference:
        Chapter 6, Formula 6.4
    """
    resistance = measured_voltage / current
    return resistance * geometric_factor


def coefficient_of_reflection(
    resistivity_1: float, 
    resistivity_2: float
) -> float:
    """
    Calculate coefficient of reflection between formation beds.
    
    Args:
        resistivity_1 (float): Resistivity of 1st formation bed in ohm·m
        resistivity_2 (float): Resistivity of 2nd formation bed in ohm·m
        
    Returns:
        float: Coefficient of reflection (dimensionless)
        
    Reference: Bassiouni, Z., 1994, Theory, Measurement, and Interpretation 
               of Well Logs. SPE Textbook Series Vol. 4. Chapter 5, Page: 96.
    """
    r1 = resistivity_1
    r2 = resistivity_2
    
    if r1 + r2 == 0:
        raise ValueError("Sum of resistivities cannot be zero")
    
    cr = (r1 - r2) / (r1 + r2)
    return cr


def compaction_correction_factor_shale(
    shale_transit_time: float,
    shale_compaction_coefficient: float = 1.0
) -> float:
    """
    Calculate compaction correction factor for sonic logs in shale lithology.
    
    Args:
        shale_transit_time (float): Adjacent shale bed's transit time in μs/ft
        shale_compaction_coefficient (float): Shale compaction coefficient
        
    Returns:
        float: Compaction correction factor (dimensionless)
        
    Reference: Core Laboratories. 2005. Formation Evaluation and Petrophysics, Page: 87.
    """
    dt_sh = shale_transit_time
    c = shale_compaction_coefficient
    
    cp = dt_sh * c / 100
    return cp


def diffuse_layer_thickness(
    dielectric_constant: float,
    temperature: float,
    ionic_strength: float
) -> float:
    """
    Calculates diffuse layer thickness in clay minerals.
    
    Args:
        dielectric_constant (float): Dielectric constant of water (dimensionless)
        temperature (float): Temperature (K)
        ionic_strength (float): Ionic strength (mol/L)
        
    Returns:
        float: Diffuse layer thickness (m)
        
    Reference:
        Chapter 6, Formula 6.13
    """
    boltzmann_constant = 1.38e-23  # J/K
    elementary_charge = 1.602e-19  # C
    permittivity_vacuum = 8.854e-12  # F/m
    avogadro = 6.022e23  # mol⁻¹
    
    debye_length = math.sqrt(
        (dielectric_constant * permittivity_vacuum * boltzmann_constant * temperature) /
        (2 * elementary_charge**2 * avogadro * ionic_strength * 1000)
    )
    
    return debye_length


# =============================================================================
# RESISTIVITY LOG CALCULATIONS
# =============================================================================

def apparent_resistivity(
    geometric_coefficient: float,
    potential_difference: float,
    current: float
) -> float:
    """
    Calculate apparent resistivity from resistivity log measurements.
    
    Args:
        geometric_coefficient (float): Geometric coefficient in m
        potential_difference (float): Potential difference between two points in V
        current (float): Current in Ampere
        
    Returns:
        float: Apparent resistivity in ohm·m
        
    Reference: Bassiouni, Z., 1994, Theory, Measurement, and Interpretation 
               of Well Logs. SPE Textbook Series Vol. 4. Chapter 5, Page: 93.
    """
    gt = geometric_coefficient
    dv = potential_difference
    i = current
    
    if i == 0:
        raise ValueError("Current cannot be zero")
    
    r = gt * dv / i
    return r


def formation_factor_archie(porosity: float, cementation_factor: float = 2.0) -> float:
    """
    Calculate formation factor using Archie's equation.
    
    Args:
        porosity (float): Porosity in fraction
        cementation_factor (float): Cementation factor (m), default 2.0
        
    Returns:
        float: Formation factor (dimensionless)
    """
    phi = porosity
    m = cementation_factor
    
    if phi <= 0:
        raise ValueError("Porosity must be positive")
    
    f = 1 / (phi**m)
    return f


def formation_factor_resistivity_logs(
    formation_resistivity: float,
    water_resistivity: float
) -> float:
    """
    Calculate formation factor from resistivity logs.
    
    Args:
        formation_resistivity (float): Formation resistivity in ohm·m
        water_resistivity (float): Formation water resistivity in ohm·m
        
    Returns:
        float: Formation factor (dimensionless)
    """
    rt = formation_resistivity
    rw = water_resistivity
    
    if rw == 0:
        raise ValueError("Water resistivity cannot be zero")
    
    f = rt / rw
    return f


def water_saturation_archie_general(
    formation_resistivity: float,
    water_resistivity: float,
    porosity: float,
    cementation_factor: float = 2.0,
    saturation_exponent: float = 2.0,
    tortuosity_factor: float = 1.0
) -> float:
    """
    Calculate water saturation using general form of Archie's equation.
    
    Args:
        formation_resistivity (float): Formation resistivity in ohm·m
        water_resistivity (float): Formation water resistivity in ohm·m
        porosity (float): Porosity in fraction
        cementation_factor (float): Cementation factor (m), default 2.0
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
    
    if phi <= 0 or rt <= 0 or rw <= 0:
        raise ValueError("Porosity, formation resistivity, and water resistivity must be positive")
    
    sw = ((a * rw) / (rt * phi**m))**(1/n)
    return max(0, min(1, sw))


def humble_equation_formation_factor(
    porosity: float,
    cementation_factor: float = 2.15,
    tortuosity_factor: float = 0.62
) -> float:
    """
    Calculate formation resistivity factor using Humble equation.
    
    Args:
        porosity (float): Porosity in fraction
        cementation_factor (float): Cementation factor, default 2.15
        tortuosity_factor (float): Tortuosity factor, default 0.62
        
    Returns:
        float: Formation resistivity factor (dimensionless)
    """
    phi = porosity
    m = cementation_factor
    a = tortuosity_factor
    
    if phi <= 0:
        raise ValueError("Porosity must be positive")
    
    f = a / (phi**m)
    return f


def simandoux_total_shale_equation(
    formation_resistivity: float,
    water_resistivity: float,
    shale_resistivity: float,
    porosity: float,
    shale_volume: float,
    cementation_factor: float = 2.0,
    saturation_exponent: float = 2.0
) -> float:
    """
    Calculate water saturation using Simandoux (total shale) equation.
    
    Args:
        formation_resistivity (float): Formation resistivity in ohm·m
        water_resistivity (float): Water resistivity in ohm·m
        shale_resistivity (float): Shale resistivity in ohm·m
        porosity (float): Porosity in fraction
        shale_volume (float): Shale volume fraction
        cementation_factor (float): Cementation factor (m), default 2.0
        saturation_exponent (float): Saturation exponent (n), default 2.0
        
    Returns:
        float: Water saturation in fraction
    """
    rt = formation_resistivity
    rw = water_resistivity
    rsh = shale_resistivity
    phi = porosity
    vsh = shale_volume
    m = cementation_factor
    n = saturation_exponent
    
    if phi <= 0 or rt <= 0 or rw <= 0:
        raise ValueError("Invalid input parameters")
    
    # Simandoux equation (simplified form)
    term1 = phi**m / rt
    term2 = vsh / rsh if rsh > 0 else 0
    
    if term1 + term2 <= 0:
        return 1.0
    
    sw = ((1 / rw) / (term1 + term2))**(1/n)
    return max(0, min(1, sw))


def tortuosity_resistivity_logs(
    formation_factor: float,
    porosity: float,
    cementation_factor: float = 2.0
) -> float:
    """
    Calculate tortuosity from resistivity logs.
    
    Args:
        formation_factor (float): Formation factor (dimensionless)
        porosity (float): Porosity in fraction
        cementation_factor (float): Cementation factor (m), default 2.0
        
    Returns:
        float: Tortuosity (dimensionless)
    """
    f = formation_factor
    phi = porosity
    m = cementation_factor
    
    if phi <= 0:
        raise ValueError("Porosity must be positive")
    
    a = f * (phi**m)
    return a


# =============================================================================
# NUCLEAR LOG CALCULATIONS
# =============================================================================

def porosity_density_log(
    bulk_density: float,
    matrix_density: float,
    fluid_density: float
) -> float:
    """
    Calculate porosity using density log data.
    
    Args:
        bulk_density (float): Bulk density from log in g/cm³
        matrix_density (float): Matrix density in g/cm³
        fluid_density (float): Fluid density in g/cm³
        
    Returns:
        float: Porosity in fraction
    """
    rho_b = bulk_density
    rho_ma = matrix_density
    rho_f = fluid_density
    
    if rho_ma - rho_f == 0:
        raise ValueError("Matrix and fluid densities cannot be equal")
    
    phi = (rho_ma - rho_b) / (rho_ma - rho_f)
    return max(0, min(1, phi))


def porosity_corrected_gas_effect(
    density_porosity: float,
    neutron_porosity: float,
    gas_correction_factor: float = 0.7
) -> float:
    """
    Calculate porosity corrected for gas effect.
    
    Args:
        density_porosity (float): Density porosity in fraction
        neutron_porosity (float): Neutron porosity in fraction
        gas_correction_factor (float): Gas correction factor, default 0.7
        
    Returns:
        float: Corrected porosity in fraction
    """
    phi_d = density_porosity
    phi_n = neutron_porosity
    k = gas_correction_factor
    
    # Gas correction using geometric mean
    phi_corr = math.sqrt(phi_d * (phi_d + phi_n) * k)
    return max(0, min(1, phi_corr))


def gamma_ray_shale_index(
    gamma_ray_log: float,
    gamma_ray_clean: float,
    gamma_ray_shale: float
) -> float:
    """
    Calculate shale index from gamma ray log.
    
    Args:
        gamma_ray_log (float): Gamma ray log reading in API units
        gamma_ray_clean (float): Clean formation gamma ray in API units
        gamma_ray_shale (float): Shale gamma ray in API units
        
    Returns:
        float: Shale index in fraction
    """
    gr = gamma_ray_log
    gr_clean = gamma_ray_clean
    gr_shale = gamma_ray_shale
    
    if gr_shale - gr_clean == 0:
        raise ValueError("Shale and clean formation gamma ray values cannot be equal")
    
    ish = (gr - gr_clean) / (gr_shale - gr_clean)
    return max(0, min(1, ish))


def effective_porosity_neutron_density(
    neutron_porosity: float,
    density_porosity: float,
    shale_volume: float,
    neutron_shale: float,
    density_shale: float
) -> float:
    """
    Calculate effective porosity from neutron and density logs.
    
    Args:
        neutron_porosity (float): Neutron porosity in fraction
        density_porosity (float): Density porosity in fraction
        shale_volume (float): Shale volume fraction
        neutron_shale (float): Neutron reading in shale in fraction
        density_shale (float): Density reading in shale in g/cm³
        
    Returns:
        float: Effective porosity in fraction
    """
    phi_n = neutron_porosity
    phi_d = density_porosity
    vsh = shale_volume
    phi_n_sh = neutron_shale
    phi_d_sh = density_shale
    
    # Correct for shale effect
    phi_n_corr = phi_n - vsh * phi_n_sh
    phi_d_corr = phi_d - vsh * phi_d_sh
    
    # Average corrected porosities
    phi_eff = (phi_n_corr + phi_d_corr) / 2
    return max(0, min(1, phi_eff))


def neutron_porosity_shale_zone(
    neutron_reading: float,
    neutron_matrix: float,
    neutron_fluid: float,
    shale_correction: float = 0.0
) -> float:
    """
    Calculate neutron porosity in shale zones.
    
    Args:
        neutron_reading (float): Neutron log reading
        neutron_matrix (float): Neutron matrix value
        neutron_fluid (float): Neutron fluid value
        shale_correction (float): Shale correction factor, default 0.0
        
    Returns:
        float: Neutron porosity in fraction
    """
    n_log = neutron_reading
    n_ma = neutron_matrix
    n_f = neutron_fluid
    corr = shale_correction
    
    if n_f - n_ma == 0:
        raise ValueError("Neutron fluid and matrix values cannot be equal")
    
    phi_n = (n_log - n_ma) / (n_f - n_ma) - corr
    return max(0, min(1, phi_n))


def composite_capture_cross_section(time_constant: float) -> float:
    """
    Calculate composite capture cross section using thermal decay time.
    
    Args:
        time_constant (float): Time required for neutron to diminish to 37% in s
        
    Returns:
        float: Composite capture cross section (dimensionless)
    """
    tau = time_constant
    
    if tau <= 0:
        raise ValueError("Time constant must be positive")
    
    s = 3.15 / tau
    return s


def atlas_neutron_lifetime_log(
    thermal_neutron_decay_time: float,
    epithermal_neutron_decay_time: float,
    formation_factor: float
) -> float:
    """
    Calculates formation properties from Atlas wireline neutron lifetime log.
    
    Args:
        thermal_neutron_decay_time (float): Thermal neutron decay time (μs)
        epithermal_neutron_decay_time (float): Epithermal neutron decay time (μs)
        formation_factor (float): Formation factor (dimensionless)
        
    Returns:
        float: Neutron lifetime parameter
        
    Reference:
        Chapter 6, Formula 6.6
    """
    thermal_term = 1 / thermal_neutron_decay_time
    epithermal_term = 1 / epithermal_neutron_decay_time
    
    return (thermal_term - epithermal_term) * formation_factor


# =============================================================================
# SPECIALIZED CALCULATIONS
# =============================================================================

def wavelength_equation(velocity: float, frequency: float) -> float:
    """
    Calculate wavelength from velocity and frequency.
    
    Args:
        velocity (float): Velocity in m/s
        frequency (float): Frequency in Hz
        
    Returns:
        float: Wavelength in m
    """
    v = velocity
    f = frequency
    
    if f == 0:
        raise ValueError("Frequency cannot be zero")
    
    wavelength = v / f
    return wavelength


def poisson_ratio_seismic(
    compressional_velocity: float,
    shear_velocity: float
) -> float:
    """
    Calculate Poisson's ratio using seismic arrival time method.
    
    Args:
        compressional_velocity (float): P-wave velocity in m/s
        shear_velocity (float): S-wave velocity in m/s
        
    Returns:
        float: Poisson's ratio (dimensionless)
    """
    vp = compressional_velocity
    vs = shear_velocity
    
    if vs == 0:
        raise ValueError("Shear velocity cannot be zero")
    
    ratio = (vp / vs)**2
    if ratio <= 2:
        raise ValueError("Invalid velocity ratio for Poisson's ratio calculation")
    
    nu = (ratio - 2) / (2 * (ratio - 1))
    return max(0, min(0.5, nu))


def water_saturation_neutron_tools(
    neutron_porosity: float,
    density_porosity: float,
    neutron_hydrocarbon: float = 0.0
) -> float:
    """
    Calculate water saturation from neutron tools.
    
    Args:
        neutron_porosity (float): Neutron porosity in fraction
        density_porosity (float): Density porosity in fraction
        neutron_hydrocarbon (float): Neutron reading in hydrocarbon zone, default 0.0
        
    Returns:
        float: Water saturation in fraction
    """
    phi_n = neutron_porosity
    phi_d = density_porosity
    phi_hc = neutron_hydrocarbon
    
    if phi_d == 0:
        return 1.0
    
    # Simplified neutron-density separation method
    sw = (phi_n - phi_hc) / phi_d
    return max(0, min(1, sw))


def effect_of_clay_on_conductivity(
    clay_conductivity: float,
    clay_volume_fraction: float,
    water_conductivity: float
) -> float:
    """
    Calculates effect of clay on formation conductivity.
    
    Args:
        clay_conductivity (float): Clay conductivity (S/m)
        clay_volume_fraction (float): Clay volume fraction (fraction)
        water_conductivity (float): Water conductivity (S/m)
        
    Returns:
        float: Total formation conductivity (S/m)
        
    Reference:
        Chapter 6, Formula 6.14
    """
    return clay_conductivity * clay_volume_fraction + water_conductivity * (1 - clay_volume_fraction)


def effective_photoelectric_cross_section(
    photoelectric_factor: float,
    bulk_density: float
) -> float:
    """
    Calculates effective photoelectric absorption cross section index.
    
    Args:
        photoelectric_factor (float): Photoelectric factor (barns/electron)
        bulk_density (float): Bulk density (g/cm³)
        
    Returns:
        float: Effective photoelectric cross section index
        
    Reference:
        Chapter 6, Formula 6.15
    """
    return photoelectric_factor * bulk_density


def electrochemical_potential_sp(
    temperature: float,
    formation_water_resistivity: float,
    mud_filtrate_resistivity: float
) -> float:
    """
    Calculates electrochemical potential for SP log.
    
    Args:
        temperature (float): Temperature (K)
        formation_water_resistivity (float): Formation water resistivity (ohm-m)
        mud_filtrate_resistivity (float): Mud filtrate resistivity (ohm-m)
        
    Returns:
        float: Electrochemical potential (mV)
        
    Reference:
        Chapter 6, Formula 6.17
    """
    gas_constant = 8.314  # J/(mol·K)
    faraday_constant = 96485  # C/mol
    
    return (gas_constant * temperature / faraday_constant) * 1000 * \
           math.log(formation_water_resistivity / mud_filtrate_resistivity)


def electron_density_index(
    bulk_density: float,
    atomic_weight: float,
    atomic_number: float
) -> float:
    """
    Calculates electron density index for gamma ray absorption logging.
    
    Args:
        bulk_density (float): Bulk density (g/cm³)
        atomic_weight (float): Average atomic weight (g/mol)
        atomic_number (float): Average atomic number (dimensionless)
        
    Returns:
        float: Electron density index (electrons/cm³)
        
    Reference:
        Chapter 6, Formula 6.19
    """
    avogadro = 6.022e23  # mol⁻¹
    return bulk_density * avogadro * atomic_number / atomic_weight


def epithermal_neutron_diffusion_coefficient(
    macroscopic_absorption_cross_section: float,
    macroscopic_transport_cross_section: float
) -> float:
    """
    Calculates epithermal neutron diffusion coefficient.
    
    Args:
        macroscopic_absorption_cross_section (float): Macroscopic absorption cross section (cm⁻¹)
        macroscopic_transport_cross_section (float): Macroscopic transport cross section (cm⁻¹)
        
    Returns:
        float: Epithermal neutron diffusion coefficient (cm)
        
    Reference:
        Chapter 6, Formula 6.20
    """
    return 1 / (3 * macroscopic_transport_cross_section * (1 + macroscopic_absorption_cross_section))


def formation_factor_dual_water_model(
    total_porosity: float,
    clay_bound_water_porosity: float,
    cementation_exponent: float = 2.0
) -> float:
    """
    Calculates formation factor using dual water model.
    
    Args:
        total_porosity (float): Total porosity (fraction)
        clay_bound_water_porosity (float): Clay-bound water porosity (fraction)
        cementation_exponent (float, optional): Cementation exponent. Defaults to 2.0.
        
    Returns:
        float: Formation factor (dimensionless)
        
    Reference:
        Chapter 6, Formula 6.23
    """
    effective_porosity = total_porosity - clay_bound_water_porosity
    if effective_porosity <= 0:
        raise ValueError("Effective porosity must be positive")
    
    return 1 / (effective_porosity**cementation_exponent)


def gamma_ray_shale_index(
    gamma_ray_reading: float,
    gamma_ray_clean: float,
    gamma_ray_shale: float
) -> float:
    """
    Calculates shale index from gamma ray log.
    
    Args:
        gamma_ray_reading (float): Gamma ray reading (API units)
        gamma_ray_clean (float): Gamma ray reading in clean formation (API units)
        gamma_ray_shale (float): Gamma ray reading in shale (API units)
        
    Returns:
        float: Shale index (fraction)
        
    Reference:
        Chapter 6, Formula 6.33
    """
    if gamma_ray_shale == gamma_ray_clean:
        return 0.0
    
    shale_index = (gamma_ray_reading - gamma_ray_clean) / (gamma_ray_shale - gamma_ray_clean)
    return max(0.0, min(1.0, shale_index))


def half_thickness_value(
    linear_absorption_coefficient: float
) -> float:
    """
    Calculates half thickness value for radiation attenuation.
    
    Args:
        linear_absorption_coefficient (float): Linear absorption coefficient (cm⁻¹)
        
    Returns:
        float: Half thickness value (cm)
        
    Reference:
        Chapter 6, Formula 6.39
    """
    return math.log(2) / linear_absorption_coefficient


def hingle_crossplot_parameter(
    resistivity_ratio: float,
    porosity: float
) -> float:
    """
    Calculates parameter for Hingle nonlinear-resistivity/linear-porosity crossplot.
    
    Args:
        resistivity_ratio (float): Formation resistivity to water resistivity ratio
        porosity (float): Porosity (fraction)
        
    Returns:
        float: Hingle crossplot parameter
        
    Reference:
        Chapter 6, Formula 6.40
    """
    return resistivity_ratio * porosity


def linear_absorption_coefficient(
    initial_intensity: float,
    transmitted_intensity: float,
    thickness: float
) -> float:
    """
    Calculates linear absorption (attenuation) coefficient.
    
    Args:
        initial_intensity (float): Initial radiation intensity
        transmitted_intensity (float): Transmitted radiation intensity
        thickness (float): Material thickness (cm)
        
    Returns:
        float: Linear absorption coefficient (cm⁻¹)
        
    Reference:
        Chapter 6, Formula 6.44
    """
    if transmitted_intensity <= 0 or initial_intensity <= transmitted_intensity:
        raise ValueError("Invalid intensity values")
    
    return math.log(initial_intensity / transmitted_intensity) / thickness


def maximum_sp_potential(
    temperature: float,
    formation_water_resistivity: float,
    mud_filtrate_resistivity: float
) -> float:
    """
    Calculates maximum potential for self-potential (SP) log.
    
    Args:
        temperature (float): Temperature (°F)
        formation_water_resistivity (float): Formation water resistivity (ohm-m)
        mud_filtrate_resistivity (float): Mud filtrate resistivity (ohm-m)
        
    Returns:
        float: Maximum SP potential (mV)
        
    Reference:
        Chapter 6, Formula 6.45
    """
    # Convert temperature to Kelvin
    temp_k = (temperature - 32) * 5/9 + 273.15
    
    # Electrochemical component
    k_value = -70.2 - 0.152 * (temperature - 77)  # Temperature correction
    
    return k_value * math.log10(formation_water_resistivity / mud_filtrate_resistivity)


def neutron_lethargy(
    initial_energy: float,
    final_energy: float
) -> float:
    """
    Calculates neutron lethargy (logarithmic energy decrement).
    
    Args:
        initial_energy (float): Initial neutron energy (eV)
        final_energy (float): Final neutron energy (eV)
        
    Returns:
        float: Neutron lethargy (dimensionless)
        
    Reference:
        Chapter 6, Formula 6.48
    """
    if initial_energy <= 0 or final_energy <= 0:
        raise ValueError("Energies must be positive")
    
    return math.log(initial_energy / final_energy)


def porosity_density_log(
    bulk_density: float,
    matrix_density: float,
    fluid_density: float = 1.0
) -> float:
    """
    Calculates porosity using density log data.
    
    Args:
        bulk_density (float): Bulk density from log (g/cm³)
        matrix_density (float): Matrix density (g/cm³)
        fluid_density (float, optional): Fluid density (g/cm³). Defaults to 1.0.
        
    Returns:
        float: Porosity (fraction)
        
    Reference:
        Chapter 6, Formula 6.56
    """
    porosity = (matrix_density - bulk_density) / (matrix_density - fluid_density)
    return max(0.0, min(1.0, porosity))


def porosity_gas_effect_correction(
    apparent_porosity: float,
    gas_saturation: float,
    correction_factor: float = 0.3
) -> float:
    """
    Calculates porosity corrected for gas effect.
    
    Args:
        apparent_porosity (float): Apparent porosity from logs (fraction)
        gas_saturation (float): Gas saturation (fraction)
        correction_factor (float, optional): Gas correction factor. Defaults to 0.3.
        
    Returns:
        float: Gas-corrected porosity (fraction)
        
    Reference:
        Chapter 6, Formula 6.57
    """
    gas_correction = correction_factor * gas_saturation
    corrected_porosity = apparent_porosity / (1 - gas_correction)
    return max(0.0, min(1.0, corrected_porosity))


def radioactive_decay_rate(
    decay_constant: float,
    number_of_atoms: float
) -> float:
    """
    Calculates rate of radioactive decay.
    
    Args:
        decay_constant (float): Decay constant (1/s)
        number_of_atoms (float): Number of radioactive atoms
        
    Returns:
        float: Decay rate (disintegrations/s)
        
    Reference:
        Chapter 6, Formula 6.59
    """
    return decay_constant * number_of_atoms


def ssp_nacl_relationship(
    temperature: float,
    formation_water_resistivity: float,
    mud_filtrate_resistivity: float
) -> float:
    """
    Calculates relationship between SSP and Rw for NaCl predominant solutions.
    
    Args:
        temperature (float): Temperature (°F)
        formation_water_resistivity (float): Formation water resistivity (ohm-m)
        mud_filtrate_resistivity (float): Mud filtrate resistivity (ohm-m)
        
    Returns:
        float: Static SP (mV)
        
    Reference:
        Chapter 6, Formula 6.62
    """
    # Temperature-dependent coefficient
    k_temp = -65.5 - 0.24 * (temperature - 77)
    
    return k_temp * math.log10(formation_water_resistivity / mud_filtrate_resistivity)


def sonic_porosity_raymer_hunt(
    transit_time_log: float,
    matrix_transit_time: float,
    fluid_transit_time: float = 189.0
) -> float:
    """
    Calculates sonic porosity using Raymer Hunt Gardner method.
    
    Args:
        transit_time_log (float): Transit time from log (μs/ft)
        matrix_transit_time (float): Matrix transit time (μs/ft)
        fluid_transit_time (float, optional): Fluid transit time (μs/ft). Defaults to 189.0.
        
    Returns:
        float: Sonic porosity (fraction)
        
    Reference:
        Chapter 6, Formula 6.70
    """
    if transit_time_log <= matrix_transit_time:
        return 0.0
    
    porosity = (transit_time_log - matrix_transit_time) / (fluid_transit_time - matrix_transit_time)
    return max(0.0, min(1.0, porosity))


def time_average_compacted_formations(
    porosity: float,
    matrix_transit_time: float,
    fluid_transit_time: float,
    compaction_factor: float = 1.67
) -> float:
    """
    Calculates time-average relation in compacted formations.
    
    Args:
        porosity (float): Porosity (fraction)
        matrix_transit_time (float): Matrix transit time (μs/ft)
        fluid_transit_time (float): Fluid transit time (μs/ft)
        compaction_factor (float, optional): Compaction factor. Defaults to 1.67.
        
    Returns:
        float: Formation transit time (μs/ft)
        
    Reference:
        Chapter 6, Formula 6.74
    """
    corrected_porosity = porosity / compaction_factor
    return matrix_transit_time + corrected_porosity * (fluid_transit_time - matrix_transit_time)


def water_saturation_neutron_tools(
    neutron_porosity: float,
    density_porosity: float,
    gas_correction_factor: float = 0.4
) -> float:
    """
    Calculates water saturation from neutron tools.
    
    Args:
        neutron_porosity (float): Neutron porosity (fraction)
        density_porosity (float): Density porosity (fraction)
        gas_correction_factor (float, optional): Gas correction factor. Defaults to 0.4.
        
    Returns:
        float: Water saturation (fraction)
        
    Reference:
        Chapter 6, Formula 6.83
    """
    if density_porosity <= 0:
        return 1.0
    
    apparent_porosity_ratio = neutron_porosity / density_porosity
    
    # Gas effect causes neutron porosity to read low relative to density porosity
    if apparent_porosity_ratio < 1.0:
        gas_saturation = (1.0 - apparent_porosity_ratio) / gas_correction_factor
        water_saturation = 1.0 - gas_saturation
    else:
        water_saturation = 1.0
    
    return max(0.0, min(1.0, water_saturation))


def wavelength_equation(
    velocity: float,
    frequency: float
) -> float:
    """
    Calculates wavelength from velocity and frequency.
    
    Args:
        velocity (float): Wave velocity (m/s)
        frequency (float): Frequency (Hz)
        
    Returns:
        float: Wavelength (m)
        
    Reference:
        Chapter 6, Formula 6.85
    """
    return velocity / frequency
