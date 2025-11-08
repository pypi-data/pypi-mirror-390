"""
Enhanced Oil Recovery and Geothermal Engineering Module

This module provides calculations for enhanced oil recovery (EOR) techniques
including steam injection, in-situ combustion, polymer flooding, carbon dioxide
injection, and geothermal well operations.

Author: PetroCalc Development Team
Source: Chapter 10 - Enhanced oil recovery and geothermal formulas and calculations
"""

import math
from typing import Tuple, Optional, Union


def areal_extent_heated_zone(
    qi: float,
    h: float,
    mr: float,
    g: float,
    dt: float,
    ms: float,
    a_s: float
) -> float:
    """
    Calculate the areal extent of heated zone in thermal recovery.
    
    Args:
        qi: Amount of Heat Injected (BTU)
        h: Height (ft)
        mr: Volumetric Heat Capacity of Reservoir (BTU/ft³°F)
        g: Dimensionless Time Function (dimensionless)
        dt: Temperature Differential (°F)
        ms: Volumetric Heat Capacity of Steam (BTU/ft³°F)
        a_s: Thermal Diffusivity (ft²/d)
    
    Returns:
        float: Area (acres)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 5, Page: 44.
    """
    area = (qi * h * mr * g) / (43560 * 4 * dt * a_s * ms**2)
    return area


def average_reservoir_temperature_cyclical_steam(
    ti: float,
    ts: float,
    f_hd: float,
    f_vd: float,
    f_pd: float
) -> float:
    """
    Calculate average reservoir temperature in a cyclical steam injection process.
    
    Args:
        ti: Initial Temperature (°F)
        ts: Temperature of Steam (°F)
        f_hd: Time-dependent Conduction Loss in Direction of Heated interval (dimensionless)
        f_vd: Time-dependent Conduction Loss Normal to Direction of Heated interval (dimensionless)
        f_pd: Time-dependent Quantity for Heat Loss by Produced Fluid (dimensionless)
    
    Returns:
        float: Average Temperature within the Heated Zone (°F)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 9, Page: 115.
    """
    ta = ti + (ts - ti) * f_vd * f_hd * (1 - 2*f_pd) / (2 - f_pd)
    return ta


def bottomhole_pressure_static_geothermal(
    density: float,
    depth: float,
    gravity: float = 32.174
) -> float:
    """
    Calculate bottomhole pressure gradient in a static geothermal well.
    
    Args:
        density: Density (lb/ft³)
        depth: Vertical Depth (ft)
        gravity: Acceleration of Gravity (ft/s²), default = 32.174
    
    Returns:
        float: Bottomhole Pressure Gradient (psi/ft)
    
    Reference:
        Ramey Jr, H. J. (1981). Reservoir Engineering Assessment of Geothermal Systems.
        Department of Petroleum Engineering, Stanford University. Page: 7.4.
    """
    dp_dd = density * gravity / (144 * gravity)  # gc = gravity in consistent units
    return dp_dd


def chromatographic_lag_polymer_flooding(
    adsorption_rate: float,
    rock_density: float,
    porosity: float,
    polymer_concentration: float,
    water_saturation: float
) -> float:
    """
    Calculate chromatographic lag in polymer flooding.
    
    Args:
        adsorption_rate: Adsorption Rate (g polymer/g rock)
        rock_density: Rock Density (g/cc)
        porosity: Porosity (fraction)
        polymer_concentration: Polymer Concentration (g/cc)
        water_saturation: Water Saturation (fraction)
    
    Returns:
        float: Chromatographic Lag (dimensionless)
    
    Reference:
        Petrowiki.org
    """
    numerator = 1
    denominator = 1 + (adsorption_rate * rock_density * (1 - porosity)) / (polymer_concentration * porosity * water_saturation)
    cl = numerator / denominator
    return cl


def cumulative_heat_injected_steam_drive(
    wi: float,
    cw: float,
    dt: float,
    f_sdh: float,
    l_vdh: float
) -> float:
    """
    Calculate cumulative heat injected for steam drive (Myhill and Stegemeier).
    
    Args:
        wi: Mass Rate of Injection of Steam into Reservoir (lb/d)
        cw: Average Specific Heat (BTU/lb°F)
        dt: Temperature Differential (°F)
        f_sdh: Steam Quality (fraction)
        l_vdh: Latent Heat of Steam (BTU/lb)
    
    Returns:
        float: Heat Injection Rate (BTU/d)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 7, Page: 76.
    """
    qi = wi * (cw * dt + f_sdh * l_vdh)
    return qi


def co2_alteration_front_battlet_gouedard(time_days: float) -> float:
    """
    Calculate depth of carbon dioxide alteration front (Battlet-Gouedard, 2006).
    
    Args:
        time_days: Time in days (d)
    
    Returns:
        float: Depth of Alteration Front (mm)
    
    Reference:
        Runar Nygaard. Waban Area Carbon-Dioxide Sequestration project. 
        Energy and Environmental Group, University of Calgary, Calgary, Alberta.
    """
    d = 0.26 * (time_days**0.5)
    return d


def co2_alteration_front_kutchko(time_days: float) -> float:
    """
    Calculate depth of carbon dioxide alteration front (Kutchko, 2008).
    
    Args:
        time_days: Time in days (d)
    
    Returns:
        float: Depth of Alteration Front (mm)
    
    Reference:
        Runar Nygaard. Waban Area Carbon-Dioxide Sequestration project. 
        Energy and Environmental Group, University of Calgary, Calgary, Alberta.
    """
    d = 0.016 * (time_days**0.5)
    return d


def dimensionless_heat_injection_rate(
    mf: float,
    mr: float,
    ht: float,
    injection_rate: float,
    a_s: float,
    ms: float,
    length: float
) -> float:
    """
    Calculate dimensionless heat injection rate (Gringarten and Sauty).
    
    Args:
        mf: Volumetric Heat Capacity of the Injected Hot Fluid (BTU/ft³°F)
        mr: Volumetric Heat Capacity of the Reservoir (BTU/ft³°F)
        ht: Height (ft)
        injection_rate: Injection Rate (ft³/d)
        a_s: Thermal Diffusivity to Overburden (ft²/d)
        ms: Volumetric Heat Capacity of Steam (BTU/ft³°F)
        length: Length (ft)
    
    Returns:
        float: Dimensionless Injection Rate (dimensionless)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 5, Page: 51.
    """
    qid = (mf * mr * ht * injection_rate) / (4 * a_s * ms**2 * length**2)
    return qid


def dimensionless_air_injection_rate_combustion(
    ia: float,
    length: float,
    thickness: float,
    u_min: float
) -> float:
    """
    Calculate dimensionless injection rate of air for in-situ combustion.
    
    Args:
        ia: Injection Rate (ft³/d)
        length: Length Between Injector and Producer in Pattern (ft)
        thickness: Formation Thickness (ft)
        u_min: Minimum Air Flux (ft/d)
    
    Returns:
        float: Dimensionless Air Injection Rate (dimensionless)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 8, Page: 100.
    """
    id_air = ia / (length * thickness * u_min)
    return id_air


def dimensionless_heat_capacity_ratio(
    rw: float,
    cw: float,
    dt: float,
    fs: float,
    lv: float,
    mr: float
) -> float:
    """
    Calculate dimensionless ratio of effective volumetric heat capacity.
    
    Args:
        rw: Density of Water (g/cc)
        cw: Specific Heat of Water (BTU/°F·mol·psi)
        dt: Temperature Differential (°F)
        fs: Steam Quality (fraction)
        lv: Latent Heat of Vaporization (BTU/lbm)
        mr: Volumetric Heat Capacity of the Reservoir (BTU/ft³°F)
    
    Returns:
        float: Dimensionless Heat Capacity Ratio (dimensionless)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 12, Page: 164.
    """
    fdh = (rw * (cw * dt + fs * lv)) / (mr * dt)
    return fdh


def dimensionless_time_coalbed_methane(
    kg: float,
    time_hours: float,
    porosity: float,
    mu_gi: float,
    cti: float,
    area: float
) -> float:
    """
    Calculate dimensionless time for semi-steady state flow in coal bed methane reservoirs.
    
    Args:
        kg: Effective Gas Compressibility (1/psi)
        time_hours: Time (h)
        porosity: Porosity (fraction)
        mu_gi: Gas Viscosity at Initial Pressure (cP)
        cti: Total Compressibility at Initial Pressure (1/psi)
        area: Drainage Area (ft²)
    
    Returns:
        float: Dimensionless Time (dimensionless)
    
    Reference:
        Ahmed, T., McKinney, P.D. 2005. Advanced Reservoir Engineering, 
        Gulf Publishing of Elsevier, Chapter: 3, Page: 221.
    """
    tda = (0.0002637 * kg * time_hours) / (porosity * mu_gi * cti * area)
    return tda


def dimensionless_time_wet_combustion(
    ms: float,
    mr: float,
    a_s: float,
    ht: float,
    time_days: float
) -> float:
    """
    Calculate dimensionless time in wet combustion by Kuo.
    
    Args:
        ms: Volumetric Heat Capacity of Steam (BTU/ft³°F)
        mr: Volumetric Heat Capacity of the Reservoir (BTU/ft³°F)
        a_s: Thermal Diffusivity of Steam to Overburden (ft²/d)
        ht: Thickness of Reservoir (ft)
        time_days: Time (d)
    
    Returns:
        float: Dimensionless Time (dimensionless)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 8, Page: 104.
    """
    td = (4 * ms**2 * a_s * time_days) / (mr**2 * ht**2)
    return td


def dykstra_parsons_coefficient(k50: float, k84_1: float) -> float:
    """
    Calculate Dykstra-Parsons coefficient for reservoir heterogeneity.
    
    Args:
        k50: Permeability at 50th percentile (mD)
        k84_1: Permeability at 84.1th percentile (mD)
    
    Returns:
        float: Dykstra-Parsons Coefficient (dimensionless)
    
    Reference:
        Willhite, G. P., 1986, Waterflooding, Vol. 3, Richardson, Texas: 
        Textbook Series, SPE, Chapter: 5, Page: 172.
    """
    v = (k50 - k84_1) / k50
    return v


def effective_transmissivity(
    kai: float,
    ha: float,
    mai: float
) -> float:
    """
    Calculate effective (apparent) transmissivity.
    
    Args:
        kai: Effective Permeability to Steam (mD)
        ha: Net Thickness of Steam Zone (ft)
        mai: Apparent Viscosity of Steam (cP)
    
    Returns:
        float: Transmissivity (mD·ft/cP)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 12, Page: 167.
    """
    tai = (kai * ha) / mai
    return tai


def steam_injection_performance_prediction(
    time: float,
    steam_rate: float,
    reservoir_area: float,
    net_thickness: float,
    oil_saturation: float,
    recovery_factor: float
) -> float:
    """
    Estimate cumulative oil production from steam drive reservoirs.
    
    Args:
        time: Time (days)
        steam_rate: Steam injection rate (bbl/d cold water equivalent)
        reservoir_area: Reservoir area (acres)
        net_thickness: Net thickness (ft)
        oil_saturation: Oil saturation (fraction)
        recovery_factor: Recovery factor (fraction)
    
    Returns:
        float: Cumulative oil produced (bbl)
    
    Note:
        This is a simplified performance prediction model.
    """
    # Convert area to ft²
    area_ft2 = reservoir_area * 43560
    
    # Calculate pore volume
    pore_volume = area_ft2 * net_thickness * 0.2  # Assuming 20% porosity
    
    # Calculate oil in place
    oil_in_place = pore_volume * oil_saturation / 5.615  # Convert ft³ to bbl
    
    # Calculate steam zone growth (simplified)
    steam_zone_volume = steam_rate * time * 5.615  # Convert bbl to ft³
    
    # Calculate oil recovery
    oil_recovered = min(oil_in_place * recovery_factor, 
                       oil_in_place * (steam_zone_volume / pore_volume))
    
    return oil_recovered


def geothermal_well_temperature(
    surface_temp: float,
    depth: float,
    geothermal_gradient: float = 0.025
) -> float:
    """
    Calculate temperature of a producing geothermal well.
    
    Args:
        surface_temp: Surface temperature (°F)
        depth: Well depth (ft)
        geothermal_gradient: Geothermal gradient (°F/ft), default = 0.025
    
    Returns:
        float: Well temperature (°F)
    
    Note:
        Uses simplified linear geothermal gradient model.
    """
    temp = surface_temp + depth * geothermal_gradient
    return temp


def oil_steam_ratio_marx_langenheim(
    oil_production_rate: float,
    steam_injection_rate: float
) -> float:
    """
    Calculate oil-steam ratio using Marx & Langenheim method.
    
    Args:
        oil_production_rate: Oil production rate (bbl/d)
        steam_injection_rate: Steam injection rate (bbl/d cold water equivalent)
    
    Returns:
        float: Oil-steam ratio (dimensionless)
    
    Reference:
        Marx, J.W. and Langenheim, R.H.: "Reservoir Heating by Hot Fluid Injection"
    """
    if steam_injection_rate == 0:
        return 0.0
    
    osr = oil_production_rate / steam_injection_rate
    return osr


def polymer_slug_size(
    pore_volume: float,
    slug_size_factor: float = 0.1
) -> float:
    """
    Calculate slug size in polymer floods.
    
    Args:
        pore_volume: Pore volume (bbl)
        slug_size_factor: Slug size as fraction of pore volume (fraction), default = 0.1
    
    Returns:
        float: Slug size (bbl)
    
    Note:
        Typical slug sizes range from 0.05 to 0.5 pore volumes.
    """
    slug_size = pore_volume * slug_size_factor
    return slug_size


def combustion_front_advancement_rate(
    air_injection_rate: float,
    pattern_area: float,
    fuel_concentration: float,
    air_fuel_ratio: float = 10.0
) -> float:
    """
    Calculate rate of advancement of combustion front in in-situ combustion.
    
    Args:
        air_injection_rate: Air injection rate (scf/d)
        pattern_area: Pattern area (acres)
        fuel_concentration: Fuel concentration (lb/ft³)
        air_fuel_ratio: Air-fuel ratio (scf air/lb fuel), default = 10.0
    
    Returns:
        float: Combustion front advancement rate (ft/d)
    
    Note:
        Simplified calculation for combustion front movement.
    """
    # Convert area to ft²
    area_ft2 = pattern_area * 43560
    
    # Calculate fuel burning rate
    fuel_burning_rate = air_injection_rate / air_fuel_ratio  # lb/d
    
    # Calculate front advancement
    front_rate = fuel_burning_rate / (area_ft2 * fuel_concentration)
    
    return front_rate


def thermal_efficiency_steam_drive(
    heat_injected: float,
    heat_remaining: float,
    heat_losses: float
) -> float:
    """
    Calculate thermal efficiency of steam drive process.
    
    Args:
        heat_injected: Total heat injected (BTU)
        heat_remaining: Heat remaining in reservoir (BTU)
        heat_losses: Heat losses to overburden/underburden (BTU)
    
    Returns:
        float: Thermal efficiency (fraction)
    
    Note:
        Thermal efficiency = (Heat remaining) / (Heat injected - Heat losses)
    """
    if heat_injected <= heat_losses:
        return 0.0
    
    efficiency = heat_remaining / (heat_injected - heat_losses)
    return min(efficiency, 1.0)


def effective_oil_transmissivity_thermal(fg: float, dp_qmax: float) -> float:
    """
    Calculate effective oil transmissivity for thermal stimulation.
    
    Args:
        fg: Geometric Factor (dimensionless)
        dp_qmax: Maximum Flow Resistance (psi/bbl/d)
    
    Returns:
        float: Transmissivity (mD·ft/cP)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 12, Page: 167.
    """
    tao = 141.2 * fg / dp_qmax
    return tao


def equivalent_atomic_hc_ratio_combustion(
    m: float,
    c_n2: float,
    c_o2: float,
    c_co2: float
) -> float:
    """
    Calculate equivalent atomic H/C ratio of fuel for in-situ combustion.
    
    Args:
        m: Mole Ratio of Carbon Monoxide to Carbon Emissions (fraction)
        c_n2: Concentration of Nitrogen (mole fraction)
        c_o2: Concentration of Oxygen (mole fraction)
        c_co2: Concentration of Carbon Dioxide (mole fraction)
    
    Returns:
        float: Equivalent Atomic H/C Ratio of Fuel (ratio)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 8, Page: 91.
    """
    x = 4 * (1 - m) * (0.27 * c_n2 - c_o2) / c_co2 + 2 * m - 4
    return x


def equivalent_volume_steam_injected_myhill_stegemeier(
    cw: float,
    tsb: float,
    ta: float,
    fsb: float,
    lvb: float,
    ti: float,
    to: float,
    fvdh: float,
    lvdh: float
) -> float:
    """
    Calculate equivalent volume of steam injected (Myhill and Stegemeier).
    
    Args:
        cw: Specific Heat of Water Steam (BTU/lb·°F)
        tsb: Steam Temperature at Boiler Outlet (°F)
        ta: Ambient Temperature (°F)
        fsb: Steam Quality (fraction)
        lvb: Latent Heat of Vaporization (BTU/lb)
        ti: Downhole Steam Injection Temperature (°F)
        to: Input Temperature (°F)
        fvdh: Quality of Steam Downhole (fraction)
        lvdh: Latent Heat of Vaporization Downhole (BTU/lb)
    
    Returns:
        float: Equivalent Volume of Steam (bbl)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 7, Page: 78.
    """
    numerator = cw * (tsb - ta) + fsb * lvb
    denominator = cw * (ti - to) + fvdh * lvdh
    ws_eq = 2.853e-6 * numerator / denominator
    return ws_eq


def equivalent_water_saturation_burned_zone_nelson(
    x: float,
    phi: float,
    ar: float,
    m: float
) -> float:
    """
    Calculate equivalent water saturation in burned zone (Nelson).
    
    Args:
        x: Equivalent H/C Molar Ratio (ratio)
        phi: Volume of Air Required to Burn through a Unit Volume (Mscf/ft³)
        ar: Volume Required to Burn through Reservoir (ft³)
        m: Ratio of Carbon Monoxide to Carbon Emissions (fraction)
    
    Returns:
        float: Water Saturation Resulting from Combustion (fraction)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 8, Page: 92.
    """
    swf = (0.319 * x * ar) / (phi * (422 * m + x))
    return swf


def cumulative_oil_displacement_estimate(
    vp: float,
    sw: float,
    siw: float
) -> float:
    """
    Calculate estimates of cumulative oil displacement.
    
    Args:
        vp: Pore Volume (bbl)
        sw: Average Water Saturation (fraction)
        siw: Interstitial Water Saturation (fraction)
    
    Returns:
        float: Cumulative Oil Displaced (bbl)
    
    Reference:
        Willhite, G. P., 1986, Waterflooding, Vol. 3, Richardson, Texas: 
        Textbook Series, SPE, Chapter: 3, Page: 65.
    """
    np = vp * (sw - siw)
    return np


def oil_displacement_rate_estimate(
    sw: float,
    siw: float,
    fs: float
) -> float:
    """
    Calculate estimates of oil displacement rate.
    
    Args:
        sw: Average Water Saturation (fraction)
        siw: Interstitial Water Saturation (fraction)
        fs: Fraction of Total Flowing Stream (fraction)
    
    Returns:
        float: Oil Displacement Rate (dimensionless)
    
    Reference:
        Willhite, G. P., 1986, Waterflooding, Vol. 3, Richardson, Texas: 
        Textbook Series, SPE, Chapter: 3, Page: 65.
    """
    qp = (sw - siw) / (1 - fs)
    return qp


def fraction_heat_injected_latent_form_steam_drive(
    cw: float,
    ti: float,
    ta: float,
    fsdh: float,
    lhc: float
) -> float:
    """
    Calculate fraction of heat injected in latent form (steam-drive).
    
    Args:
        cw: Specific Heat of Water (BTU/lbm·°F)
        ti: Injection Temperature (°F)
        ta: Ambient Temperature (°F)
        fsdh: Steam Quality (fraction)
        lhc: Latent Heat of Condensation (BTU/lbm)
    
    Returns:
        float: Fraction of Heat Injected in Latent Form (fraction)
    
    Reference:
        Pratts, M. (1986). Thermal Recovery Monograph Vol. 7. 
        Society of Petroleum Engineers, Houston, Page: 77.
    """
    fhv = 1 / (1 + cw * (ti - ta) / (fsdh * lhc))
    return fhv


def heat_injection_rate_steam_drive(
    wi: float,
    cw: float,
    ti: float,
    ta: float,
    fsdh: float,
    lhc: float
) -> float:
    """
    Calculate heat injection rate (steam-drive).
    
    Args:
        wi: Boiler Feed Water Rate (B/d)
        cw: Specific Heat Capacity of Water (BTU/lbm·°F)
        ti: Injection Temperature (°F)
        ta: Ambient Temperature (°F)
        fsdh: Steam Quality (fraction)
        lhc: Latent Heat of Condensation (BTU/lbm)
    
    Returns:
        float: Heat Injection Rate (BTU/d)
    
    Reference:
        Pratts, M. (1986). Thermal Recovery Monograph Vol. 7. 
        Society of Petroleum Engineers, Houston, Page: 76.
    """
    qi = wi * 62.4 * 5.615 * (cw * (ti - ta) + fsdh * lhc)
    return qi


def steam_drive_cumulative_oil_production(
    phi: float,
    hn: float,
    ht: float,
    soi: float,
    sor: float,
    ec: float,
    vs: float
) -> float:
    """
    Calculate cumulative oil production from steam-drive reservoirs.
    
    Args:
        phi: Porosity (fraction)
        hn: Net Thickness (ft)
        ht: Gross Thickness (ft)
        soi: Initial Oil Saturation (fraction)
        sor: Residual Oil Saturation (fraction)
        ec: Capture Efficiency (fraction)
        vs: Volume of Steam in Reservoir (ac·ft)
    
    Returns:
        float: Cumulative Oil Produced (BBL)
    
    Reference:
        Pratts, M. (1986). Thermal Recovery Monograph Vol. 7. 
        Society of Petroleum Engineers, Houston, Page: 75.
    """
    np = 7758 * phi * (hn / ht) * (soi - sor) * ec * vs
    return np


def steam_drive_volume_in_reservoir(
    qi: float,
    t: float,
    ehs: float,
    ti: float,
    ta: float
) -> float:
    """
    Calculate volume of steam in reservoir for steam drive.
    
    Args:
        qi: Heat Injection Rate (BTU/d)
        t: Injection Time (d)
        ehs: Thermal Efficiency of Steam Zone (dimensionless)
        ti: Injection Temperature (°F)
        ta: Ambient Temperature (°F)
    
    Returns:
        float: Gross Volume of Steam in Reservoir (ac·ft)
    
    Reference:
        Pratts, M. (1986). Thermal Recovery Monograph Vol. 7. 
        Society of Petroleum Engineers, Houston, Page: 76.
    """
    vs = (qi * t * ehs) / (38.1 * 43560 * (ti - ta))
    return vs


def steady_state_five_spot_injection_rate(
    k: float,
    h: float,
    m: float,
    area: float,
    rw: float,
    pi: float,
    pb: float
) -> float:
    """
    Calculate steady-state five-spot injection rate (steam-drive).
    
    Args:
        k: Permeability (mD)
        h: Pay zone Thickness (ft)
        m: Viscosity (cP)
        area: Area Per Pattern (acre)
        rw: Wellbore Radius (ft)
        pi: Injection Pressure (psi)
        pb: Borehole Pressure (psi)
    
    Returns:
        float: Injection Rate (BBL/d)
    
    Reference:
        Pratts, M. (1986). Thermal Recovery Monograph Vol. 7. 
        Society of Petroleum Engineers, Houston, Page: 83.
    """
    import math
    
    numerator = 7.082e-3 * math.pi * k * h / m
    denominator = math.log(208.71 * area**0.5 / rw) - 0.964
    injection_rate = numerator / denominator * (pi - pb)
    return injection_rate


def volume_steam_injection_steam_drive(
    cw: float,
    tsb: float,
    ta: float,
    fsb: float,
    lvb: float,
    tidh: float,
    ti: float,
    fsdh: float,
    lvdh: float
) -> float:
    """
    Calculate volume of steam injection (steam-drive).
    
    Args:
        cw: Specific Heat Capacity of Water (BTU/LBM·°F)
        tsb: Temperature of Steam at Boiler Outlet (°F)
        ta: Ambient Temperature (°F)
        fsb: Fraction of Steam at Boiler Outlet (fraction)
        lvb: Latent Heat of Vaporization at Boiler Outlet (BTU/lbm)
        tidh: Injection Temperature Down Hole (°F)
        ti: Injection Temperature (°F)
        fsdh: Fraction of Steam Down Hole (fraction)
        lvdh: Latent Heat of Vaporization Down Hole (BTU/lbm)
    
    Returns:
        float: Volume of Steam injected, as Water Equivalent (BBL/d)
    
    Reference:
        Pratts, M. (1986). Thermal Recovery Monograph Vol. 7. 
        Society of Petroleum Engineers, Houston, Page: 78.
    """
    numerator = cw * (tsb - ta) + fsb * lvb
    denominator = cw * (tidh - ti) + fsdh * lvdh
    ws_eq = 2.853e-6 * numerator / denominator
    return ws_eq


def fraction_heat_latent_form_myhill_stegemeier(
    h: float,
    ht: float,
    k: float,
    kt: float
) -> float:
    """
    Calculate fraction of heat injected in latent form (Myhill and Stegemeier).
    
    Args:
        h: Height (ft)
        ht: Cumulative Height (ft)
        k: Permeability (mD)
        kt: Cumulative Permeability (mD)
    
    Returns:
        float: FMO (dimensionless)
    
    Reference:
        Ehrlich, R., 2016. PTE 531 Enhanced Oil Recovery. 
        University of Southern California Lecture Notes.
    """
    fmo = (1 / ht) * (h + (kt * ht - k * h) / k)
    return fmo


def fraction_injected_heat_remaining_reservoir(
    qi: float,
    q: float
) -> float:
    """
    Calculate fraction of injected heat remaining in reservoir.
    
    Args:
        qi: Total Heat Injected (BTU)
        q: Total Heat Remaining (BTU)
    
    Returns:
        float: Fraction of Injected Heat Remaining (fraction)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 5, Page: 44.
    """
    eh = q / qi
    return eh


def fractional_flow_water_hot_floods(
    mobility_ratio: float
) -> float:
    """
    Calculate fractional flow of water in hot floods.
    
    Args:
        mobility_ratio: Mobility Ratio of the Co-flowing Fluids (dimensionless)
    
    Returns:
        float: Fractional Flow (dimensionless)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 6, Page: 60.
    """
    fw = 1 / (1 + (1 / mobility_ratio))
    return fw


def growth_steam_heated_area_marx_langenheim(
    qi: float,
    td: float,
    et: float,
    temp_diff: float,
    mr: float,
    h: float
) -> float:
    """
    Calculate growth of steam-heated area (Marx-Langenheim).
    
    Args:
        qi: Injected Heat Content (BTU)
        td: Dimensionless Time (dimensionless)
        et: Error Function of square root of dimensionless function (dimensionless)
        temp_diff: Temperature Differential (°F)
        mr: Volumetric Heat Capacity of the Reservoir (BTU/ft³·°F)
        h: Height (ft)
    
    Returns:
        float: Growth of Steam Zone (ac/d)
    
    Reference:
        Michael Prats. Thermal recovery. Society of Petroleum Engineers. 
        New York. 1986, Page: 61.
    """
    import math
    
    area = (qi * math.exp(td) * et) / (43560 * temp_diff * mr * h)
    return area


def heat_loss_incremental_well_length(
    ts: float,
    te: float,
    k_thermal: float,
    f_t: float,
    dy: float
) -> float:
    """
    Calculate heat loss over an incremental length of a well (two-phase flow).
    
    Args:
        ts: Temperature in the Well (Saturation Temperature) (°F)
        te: Undisturbed Formation Temperature (°F)
        k_thermal: Thermal Conductivity of Earth (BTU/(ft·d·°F))
        f_t: Dimensionless Time Function for Transient Heat Transfer (dimensionless)
        dy: Distance increment (ft)
    
    Returns:
        float: Heat Loss over an Incremental Length (BTU/h)
    
    Reference:
        Ramey Jr, H. J. (1981). Reservoir Engineering Assessment of Geothermal Systems.
        Department of Petroleum Engineering, Stanford University. Page: 6.12.
    """
    import math
    
    dq = (2 * math.pi * k_thermal * (ts - te) / f_t) * dy
    return dq


def heat_ratio_geothermal_reservoir(
    porosity: float,
    rw: float,
    cw: float,
    rr: float,
    cr: float
) -> float:
    """
    Calculate heat ratio of contents in a geothermal reservoir.
    
    Args:
        porosity: Porosity (dimensionless)
        rw: Water Density (kg/m³)
        cw: Performance Coefficient of Water (KJ/kg·°C)
        rr: Rock Density (kg/m³)
        cr: Rock Heat Capacity (KJ/kg·°C)
    
    Returns:
        float: Heat Ratio (dimensionless)
    
    Reference:
        Ramey Jr, H. J. (1981). Reservoir Engineering Assessment of Geothermal Systems.
        Department of Petroleum Engineering, Stanford University. Page: 9.6.
    """
    hw_ht = (rw * cw * porosity) / (rw * cw * porosity + rr * cr * (1 - porosity))
    return hw_ht


def heat_released_insitu_combustion_burger_sahuguet(
    m: float,
    x: float
) -> float:
    """
    Calculate heat released during in-situ combustion (Burger & Sahuguet).
    
    Args:
        m: Molar Ratio of H/C Emission (fraction)
        x: Proportion of Carbon Monoxide to Carbon Emissions (fraction)
    
    Returns:
        float: Heat Released (BTU/SCF)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 8, Page: 93.
    """
    dh_a = (94 - 67.9 * m + 31.2 * x) / (1 - 0.5 * m + 0.25 * x)
    return dh_a


def heat_remaining_reservoir_marx_langenheim(
    qi: float,
    mr: float,
    h: float,
    g: float,
    a_s: float,
    ms: float
) -> float:
    """
    Calculate heat remaining in reservoir (Marx and Langenheim).
    
    Args:
        qi: Total Heat Injected (BTU)
        mr: Volumetric Heat Capacity of Reservoir (BTU/ft³·°F)
        h: Height (ft)
        g: Dimensionless Time Constant (dimensionless)
        a_s: Steam Diffusivity (ft²/d)
        ms: Volumetric Heat Capacity of Adjacent Formations (BTU/ft³·°F)
    
    Returns:
        float: Heat Remaining in Reservoir (BTU)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 5, Page: 44.
    """
    q = qi * (mr**2 * h**2 * g) / (4 * a_s * ms**2)
    return q


def horizontal_well_breakthrough_time_bottom_water_drive(
    porosity: float,
    swc: float,
    soir: float,
    es: float,
    kh: float,
    kv: float,
    h: float,
    qo: float,
    bo: float
) -> Tuple[float, float]:
    """
    Calculate horizontal well breakthrough time in bottom-water-drive reservoir.
    
    Args:
        porosity: Porosity (fraction)
        swc: Connate Water Saturation (fraction)
        soir: Residual Oil Saturation (fraction)
        es: Sweep Efficiency (dimensionless)
        kh: Horizontal Permeability (mD)
        kv: Vertical Permeability (mD)
        h: Oil Column Thickness (ft)
        qo: Flow Rate (STB/d)
        bo: Oil Formation Volume Factor (RB/STB)
    
    Returns:
        Tuple[float, float]: (Saturation Constant, Water Breakthrough Time in days)
    
    Reference:
        Joshi, S. D. 1991, Horizontal Well Technology. Tulsa, Oklahoma: 
        PennWell Publishing Company. Chapter: 8, Page: 295.
    """
    fd = porosity * (1 - swc - soir)
    tbt = fd * h**3 * es * (kh / kv) / (5.615 * qo * bo)
    return fd, tbt


def ignition_delay_time_insitu_combustion(
    mr: float,
    ta: float,
    n: float,
    r_gas: float,
    e_activation: float,
    dh_a: float,
    porosity: float,
    so: float,
    ro: float,
    ac: float,
    po2: float
) -> float:
    """
    Calculate ignition delay time in in-situ combustion.
    
    Args:
        mr: Volumetric Heat Capacity of Reservoir (BTU/ft³·K)
        ta: Initial Absolute Temperature (K)
        n: exponent
        r_gas: Gas Constant (BTU/mol·K·psi)
        e_activation: Activation Energy (BTU/K·mol)
        dh_a: Heat Generated by Oxygen (BTU)
        porosity: Porosity (fraction)
        so: Saturation of Oil (fraction)
        ro: Density (g/cc)
        ac: Pre Exponential Constant (1/psi·K)
        po2: Partial Pressure of Oxygen (psi)
    
    Returns:
        float: Ignition Delay (s)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 8, Page: 95.
    """
    import math
    
    numerator = 2.04e-7 * mr * ta**2 * (1 + 2 * r_gas * ta / e_activation) * r_gas * math.exp(e_activation / (r_gas * ta))
    denominator = e_activation * dh_a * porosity * so * ro * ac * po2**n
    tig = numerator / denominator
    return tig


def injected_air_required_burn_reservoir_nelson_mcniel(
    ar_base: float,
    tsc_ab: float,
    tab: float,
    psc_ab: float,
    pinj_ab: float,
    porosity: float,
    eo2: float
) -> float:
    """
    Calculate injected air required to burn through unit bulk of reservoir (Nelson and McNiel).
    
    Args:
        ar_base: Air Required to Burn through Reservoir (MSCF/ft³)
        tsc_ab: Temperature at Standard Condition (K)
        tab: Temperature at Absolute Condition (K)
        psc_ab: Pressure at Standard Condition (psi)
        pinj_ab: Pressure at Absolute Condition (psi)
        porosity: Porosity (fraction)
        eo2: Utilization Efficiency of Oxygen (fraction)
    
    Returns:
        float: Injected Air Required (MSCF/ft³)
    
    Reference:
        Michael Prats. Thermal recovery. Society of Petroleum Engineers. 
        New York. 1986, Page: 96.
    """
    ar = (ar_base + 1e-3 * (tsc_ab / tab) * (pinj_ab / psc_ab) * porosity) / eo2
    return ar


def mass_fuel_burned_reservoir_volume_nelson_mcniel(
    phi_e: float,
    porosity: float,
    me: float
) -> float:
    """
    Calculate mass of fuel burned per unit bulk reservoir volume (Nelson and McNiel).
    
    Args:
        phi_e: Effective Porosity (fraction)
        porosity: Porosity (fraction)
        me: Mass of Fuel Burned per Unit Bulk Volume in Lab (lbm/ft³)
    
    Returns:
        float: Mass of Fuel Burned per Unit Bulk Reservoir Volume (lbm/ft³)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 8, Page: 89.
    """
    mr = ((1 - porosity) / (1 - phi_e)) * me
    return mr


def minimum_air_flux_fire_front_nelson_mcniel(
    ar: float,
    eo2: float
) -> float:
    """
    Calculate minimum air flux required for advance of fire front (Nelson and McNiel).
    
    Args:
        ar: Air Required to Burn Unit Volume of Reservoir (MSCF/ft³)
        eo2: Oxygen Consumption Efficiency (fraction)
    
    Returns:
        float: Minimum Air Flux (SCF/ft²·d)
    
    Reference:
        Prats, M. 1986. Thermal Recovery. Society of Petroleum Engineers, 
        New York, Chapter: 8, Page: 100.
    """
    umin = 0.125 * ar / eo2
    return umin


def oil_breakthrough_newly_swept_zone(
    pv: float,
    deas: float,
    swbt: float,
    swi: float
) -> float:
    """
    Calculate oil breakthrough in newly swept zone.
    
    Args:
        pv: Pore Volume (dimensionless)
        deas: Areal Sweep Efficiency from New Swept Zone (fraction)
        swbt: Water Saturation at Breakthrough in Swept Zone (fraction)
        swi: Initial Water Saturation (fraction)
    
    Returns:
        float: Oil Volume at Breakthrough in New Swept Zones (bbl)
    
    Reference:
        Ehrlich Enhanced Oil Recovery, PTE 531, University of Southern California 
        Lecture Notes, 2016.
    """
    onsz = pv * deas * (swbt - swi)
    return onsz
