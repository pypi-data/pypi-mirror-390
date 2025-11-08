"""
Economic calculations for petroleum engineering.

This module contains functions for economic analysis including:
- Net Present Value (NPV) calculations
- Discounted Cash Flow (DCF) analysis
- Economic indicators
- Cost estimation
- Project economics
"""

import math
from typing import Union, Tuple, Optional, List


def net_present_value(
    cash_flows: List[float],
    discount_rate: float,
    initial_investment: float = 0
) -> float:
    """
    Calculates Net Present Value (NPV) of a project.
    
    Args:
        cash_flows (List[float]): List of annual cash flows
        discount_rate (float): Discount rate as decimal (e.g., 0.1 for 10%)
        initial_investment (float): Initial investment (default 0)
        
    Returns:
        float: Net Present Value
    """
    npv = -initial_investment
    
    for i, cash_flow in enumerate(cash_flows):
        npv += cash_flow / (1 + discount_rate)**(i + 1)
    
    return npv


def internal_rate_of_return(
    cash_flows: List[float],
    initial_investment: float,
    tolerance: float = 0.001
) -> float:
    """
    Calculates Internal Rate of Return (IRR) using iterative method.
    
    Args:
        cash_flows (List[float]): List of annual cash flows
        initial_investment (float): Initial investment
        tolerance (float): Tolerance for convergence (default 0.001)
        
    Returns:
        float: Internal Rate of Return as decimal
    """
    # Initial guess
    irr_low = 0.0
    irr_high = 1.0
    
    # Find an upper bound where NPV is negative
    while net_present_value(cash_flows, irr_high, initial_investment) > 0:
        irr_high *= 2
        if irr_high > 10:  # Prevent infinite loop
            return float('nan')
    
    # Bisection method
    for _ in range(100):  # Maximum iterations
        irr_mid = (irr_low + irr_high) / 2
        npv_mid = net_present_value(cash_flows, irr_mid, initial_investment)
        
        if abs(npv_mid) < tolerance:
            return irr_mid
        
        if npv_mid > 0:
            irr_low = irr_mid
        else:
            irr_high = irr_mid
    
    return irr_mid


def discounted_payback_period(
    cash_flows: List[float],
    discount_rate: float,
    initial_investment: float
) -> float:
    """
    Calculates discounted payback period.
    
    Args:
        cash_flows (List[float]): List of annual cash flows
        discount_rate (float): Discount rate as decimal
        initial_investment (float): Initial investment
        
    Returns:
        float: Discounted payback period in years
    """
    cumulative_pv = -initial_investment
    
    for i, cash_flow in enumerate(cash_flows):
        pv_cash_flow = cash_flow / (1 + discount_rate)**(i + 1)
        cumulative_pv += pv_cash_flow
        
        if cumulative_pv >= 0:
            # Interpolate to find exact payback period
            previous_cumulative = cumulative_pv - pv_cash_flow
            fraction = -previous_cumulative / pv_cash_flow
            return i + 1 + fraction
    
    return float('inf')  # Never pays back


def profitability_index(
    cash_flows: List[float],
    discount_rate: float,
    initial_investment: float
) -> float:
    """
    Calculates Profitability Index (PI).
    
    Args:
        cash_flows (List[float]): List of annual cash flows
        discount_rate (float): Discount rate as decimal
        initial_investment (float): Initial investment
        
    Returns:
        float: Profitability Index
    """
    if initial_investment == 0:
        return float('inf')
    
    pv_cash_flows = sum(cf / (1 + discount_rate)**(i + 1) for i, cf in enumerate(cash_flows))
    
    return pv_cash_flows / initial_investment


def oil_revenue_calculation(
    production_rate: float,
    oil_price: float,
    royalty_rate: float = 0.125,
    operating_cost_per_barrel: float = 15
) -> float:
    """
    Calculates annual oil revenue.
    
    Args:
        production_rate (float): Oil production rate in bbl/day
        oil_price (float): Oil price in $/bbl
        royalty_rate (float): Royalty rate as decimal (default 12.5%)
        operating_cost_per_barrel (float): Operating cost in $/bbl (default 15)
        
    Returns:
        float: Annual net revenue in $
    """
    annual_production = production_rate * 365
    gross_revenue = annual_production * oil_price
    royalty = gross_revenue * royalty_rate
    operating_costs = annual_production * operating_cost_per_barrel
    
    net_revenue = gross_revenue - royalty - operating_costs
    
    return net_revenue


def gas_revenue_calculation(
    production_rate: float,
    gas_price: float,
    royalty_rate: float = 0.125,
    operating_cost_per_mcf: float = 1.5
) -> float:
    """
    Calculates annual gas revenue.
    
    Args:
        production_rate (float): Gas production rate in Mscf/day
        gas_price (float): Gas price in $/Mscf
        royalty_rate (float): Royalty rate as decimal (default 12.5%)
        operating_cost_per_mcf (float): Operating cost in $/Mscf (default 1.5)
        
    Returns:
        float: Annual net revenue in $
    """
    annual_production = production_rate * 365
    gross_revenue = annual_production * gas_price
    royalty = gross_revenue * royalty_rate
    operating_costs = annual_production * operating_cost_per_mcf
    
    net_revenue = gross_revenue - royalty - operating_costs
    
    return net_revenue


def drilling_cost_estimation(
    well_depth: float,
    hole_diameter: float,
    day_rate: float = 25000,
    drilling_days_per_1000ft: float = 2.5
) -> float:
    """
    Estimates drilling cost for a well.
    
    Args:
        well_depth (float): Well depth in ft
        hole_diameter (float): Average hole diameter in inches
        day_rate (float): Rig day rate in $/day (default 25,000)
        drilling_days_per_1000ft (float): Drilling days per 1000 ft (default 2.5)
        
    Returns:
        float: Estimated drilling cost in $
    """
    drilling_days = (well_depth / 1000) * drilling_days_per_1000ft
    
    # Complexity factor based on diameter
    if hole_diameter > 12:
        complexity_factor = 1.3
    elif hole_diameter > 8:
        complexity_factor = 1.1
    else:
        complexity_factor = 1.0
    
    drilling_cost = drilling_days * day_rate * complexity_factor
    
    return drilling_cost


def completion_cost_estimation(
    well_depth: float,
    completion_type: str = "conventional",
    number_of_stages: int = 1
) -> float:
    """
    Estimates completion cost for a well.
    
    Args:
        well_depth (float): Well depth in ft
        completion_type (str): Type of completion ("conventional", "hydraulic_fracturing")
        number_of_stages (int): Number of fracturing stages (default 1)
        
    Returns:
        float: Estimated completion cost in $
    """
    base_cost = well_depth * 50  # $50 per foot base cost
    
    if completion_type.lower() == "hydraulic_fracturing":
        frac_cost = number_of_stages * 150000  # $150k per stage
        total_cost = base_cost + frac_cost
    else:
        total_cost = base_cost
    
    return total_cost


def abandonment_cost_estimation(well_depth: float, offshore: bool = False) -> float:
    """
    Estimates well abandonment cost.
    
    Args:
        well_depth (float): Well depth in ft
        offshore (bool): Whether well is offshore (default False)
        
    Returns:
        float: Estimated abandonment cost in $
    """
    base_cost = well_depth * 25  # $25 per foot
    
    if offshore:
        base_cost *= 3  # Offshore factor
    
    # Minimum abandonment cost
    return max(100000, base_cost)


# =============================================================================
# CHAPTER 7: PETROLEUM ECONOMICS FORMULAS
# =============================================================================

def compound_interest(
    principal: float,
    nominal_rate: float,
    compounding_periods: int,
    time_years: float
) -> float:
    """
    Calculate compound interest.
    
    Args:
        principal (float): Principal amount in currency units
        nominal_rate (float): Nominal interest rate as fraction per year
        compounding_periods (int): Compounding periods per year (1=annually, 2=semi-annually, 4=quarterly, 12=monthly)
        time_years (float): Loan period or investment period in years
        
    Returns:
        float: Compound interest in currency units
        
    Reference: Mian, M.A. 2011. Project Economics and Decision Analysis Volume 1
    """
    p = principal
    i_n = nominal_rate
    m = compounding_periods
    t = time_years
    
    if p <= 0 or m <= 0:
        raise ValueError("Principal and compounding periods must be positive")
    
    compound_amount = p * (1 + i_n/m)**(m*t)
    interest = compound_amount - p
    return interest


def effective_interest_rate(nominal_rate: float, compounding_periods: int) -> float:
    """
    Calculate effective interest rate for periodic compounding.
    
    Args:
        nominal_rate (float): Nominal interest rate as fraction
        compounding_periods (int): Number of compounding periods per year
        
    Returns:
        float: Effective interest rate as fraction
        
    Reference: Mian, M.A. 2011. Project Economics and Decision Analysis Volume 1
    """
    i_n = nominal_rate
    m = compounding_periods
    
    if m <= 0:
        raise ValueError("Compounding periods must be positive")
    
    i_e = (1 + i_n/m)**m - 1
    return i_e


def future_value_annuity(
    annuity: float,
    effective_rate: float,
    time_years: float
) -> float:
    """
    Calculate future value of an annuity.
    
    Args:
        annuity (float): Annuity payment in currency units
        effective_rate (float): Effective interest rate as fraction
        time_years (float): Time in years
        
    Returns:
        float: Future value of annuity in currency units
        
    Reference: Mian, M.A. 2011. Project Economics and Decision Analysis Volume 1
    """
    av = annuity
    i_e = effective_rate
    t = time_years
    
    if i_e == 0:
        return av * t
    
    fv = av * (((1 + i_e)**t - 1) / i_e)
    return fv


def present_value_annuity(
    annuity: float,
    effective_rate: float,
    time_years: float
) -> float:
    """
    Calculate present value of an annuity.
    
    Args:
        annuity (float): Annuity payment in currency units
        effective_rate (float): Effective interest rate as fraction
        time_years (float): Time in years
        
    Returns:
        float: Present value of annuity in currency units
        
    Reference: Mian, M.A. 2011. Project Economics and Decision Analysis Volume 1
    """
    av = annuity
    i_e = effective_rate
    t = time_years
    
    if i_e == 0:
        return av * t
    
    pv = av * ((1 - (1 + i_e)**(-t)) / i_e)
    return pv


def future_value_present_sum(
    present_value: float,
    effective_rate: float,
    time_years: float
) -> float:
    """
    Calculate future value of a present sum.
    
    Args:
        present_value (float): Present value in currency units
        effective_rate (float): Effective interest rate as fraction
        time_years (float): Time in years
        
    Returns:
        float: Future value in currency units
        
    Reference: Mian, M.A. 2011. Project Economics and Decision Analysis Volume 1
    """
    pv = present_value
    i_e = effective_rate
    t = time_years
    
    fv = pv * (1 + i_e)**t
    return fv


def cost_depletion(
    adjusted_basis: float,
    units_sold: float,
    remaining_reserves: float
) -> float:
    """
    Calculate cost depletion for tax purposes.
    
    Args:
        adjusted_basis (float): Adjusted basis for the taxable year in currency units
        units_sold (float): Number of units sold in that year
        remaining_reserves (float): Number of remaining reserves at end of taxable year
        
    Returns:
        float: Cost depletion in currency units
        
    Reference: Mian, M.A. 2011. Project Economics and Decision Analysis Volume 1
    """
    ab = adjusted_basis
    q = units_sold
    rr = remaining_reserves
    
    if rr + q == 0:
        raise ValueError("Sum of remaining reserves and units sold cannot be zero")
    
    cd = ab * (q / (rr + q))
    return cd


def exploration_efficiency(
    initial_efficiency: float,
    ratio_constant: float,
    total_meterage_drilled: float
) -> float:
    """
    Calculate exploration efficiency per unit meterage.
    
    Args:
        initial_efficiency (float): Exploration efficiency at initial conditions in bbl/ft
        ratio_constant (float): Ratio constant (dimensionless)
        total_meterage_drilled (float): Total meterage drilled up to date of discovery in ft
        
    Returns:
        float: Exploration efficiency per unit meterage in bbl/ft
        
    Reference: Serpen, U., Petroleum Economics, Course Notes, ITU
    """
    e0 = initial_efficiency
    a = ratio_constant
    fd = total_meterage_drilled
    
    e = e0 * math.exp(a * fd)
    return e


def cumulative_interest_operational_expenses(
    interest_rate: float,
    daily_expenses: float,
    operating_days: float
) -> float:
    """
    Calculate cumulative interest on operational expenses during well lifetime.
    
    Args:
        interest_rate (float): Interest rate as percentage
        daily_expenses (float): Operational expenses in $/day
        operating_days (float): Operating time in days
        
    Returns:
        float: Cumulative interest on operation expenses in $
        
    Reference: Saydam, T., (1967). Principles of Hydraulic Fracturing
    """
    a = interest_rate / 100  # Convert percentage to fraction
    l = daily_expenses
    t = operating_days
    
    rc = (a * l * t**2) / 2
    return rc


def unknown_interest_rate(
    future_amount: float,
    principal: float,
    time_years: float
) -> float:
    """
    Calculate unknown interest rate from future and present values.
    
    Args:
        future_amount (float): Amount to be paid after end of t years
        principal (float): Amount borrowed (principal)
        time_years (float): Time period in years
        
    Returns:
        float: Interest rate as fraction
        
    Reference: Mian, M.A. 2011. Project Economics and Decision Analysis Volume 1
    """
    f = future_amount
    p = principal
    t = time_years
    
    if p <= 0 or t <= 0:
        raise ValueError("Principal and time must be positive")
    
    i = math.exp(math.log(f/p) / t) - 1
    return i


def average_annual_rate_of_return(
    initial_capital: float,
    total_undiscounted_cash_flow: float,
    present_worth_factor: float
) -> float:
    """
    Calculate average annual rate of return.
    
    Args:
        initial_capital (float): Initial investment/capital in $
        total_undiscounted_cash_flow (float): Total net undiscounted cash flow during project in $
        present_worth_factor (float): Present worth factor (dimensionless)
        
    Returns:
        float: Annual average rate of return as fraction
        
    Reference: Serpen, U., Petroleum Economics, Course Notes, ITU
    """
    c = initial_capital
    e = total_undiscounted_cash_flow
    d = present_worth_factor
    
    if c == 0 or d == 1:
        raise ValueError("Invalid parameters for rate of return calculation")
    
    r = ((d * e / c - 1) / (1 - d))
    return r


def payback_period_simple(
    initial_investment: float,
    annual_cash_flow: float
) -> float:
    """
    Calculate simple payback period.
    
    Args:
        initial_investment (float): Initial investment in currency units
        annual_cash_flow (float): Annual cash flow in currency units
        
    Returns:
        float: Payback period in years
    """
    if annual_cash_flow <= 0:
        raise ValueError("Annual cash flow must be positive")
    
    payback = initial_investment / annual_cash_flow
    return payback


def profitability_index(
    present_value_cash_flows: float,
    initial_investment: float
) -> float:
    """
    Calculate profitability index.
    
    Args:
        present_value_cash_flows (float): Present value of future cash flows
        initial_investment (float): Initial investment
        
    Returns:
        float: Profitability index
    """
    if initial_investment <= 0:
        raise ValueError("Initial investment must be positive")
    
    pi = present_value_cash_flows / initial_investment
    return pi


def break_even_oil_price(
    total_costs: float,
    production_volume: float,
    operating_costs_per_barrel: float = 0.0
) -> float:
    """
    Calculate break-even oil price.
    
    Args:
        total_costs (float): Total project costs in $
        production_volume (float): Total production volume in barrels
        operating_costs_per_barrel (float): Operating costs per barrel in $/bbl
        
    Returns:
        float: Break-even oil price in $/bbl
    """
    if production_volume <= 0:
        raise ValueError("Production volume must be positive")
    
    break_even_price = (total_costs / production_volume) + operating_costs_per_barrel
    return break_even_price


def lease_operating_expense_per_barrel(
    monthly_operating_cost: float,
    monthly_production: float
) -> float:
    """
    Calculate lease operating expense per barrel.
    
    Args:
        monthly_operating_cost (float): Monthly operating cost in $
        monthly_production (float): Monthly production in barrels
        
    Returns:
        float: Operating expense per barrel in $/bbl
    """
    if monthly_production <= 0:
        raise ValueError("Monthly production must be positive")
    
    opex_per_barrel = monthly_operating_cost / monthly_production
    return opex_per_barrel


def acceptable_reliability_level(
    binomial_probabilities: List[float],
    field_probabilities: List[float]
) -> float:
    """
    Calculate acceptable reliability level for petroleum exploration.
    
    Args:
        binomial_probabilities (List[float]): Binomial probabilities of discovering X number of fields
        field_probabilities (List[float]): Probabilities of fields containing minimum F barrels
        
    Returns:
        float: Acceptable reliability level (dimensionless)
    """
    if len(binomial_probabilities) != len(field_probabilities):
        raise ValueError("Probability arrays must have the same length")
    
    return sum(p_x * p_f for p_x, p_f in zip(binomial_probabilities, field_probabilities))


def additional_production_estimation(
    fields_discovered: int,
    additional_fields_estimated: int,
    average_annual_production: float
) -> float:
    """
    Estimate additional production with new wells.
    
    Args:
        fields_discovered (int): Number of fields discovered to date in selected field class
        additional_fields_estimated (int): Number of fields estimated to be discovered
        average_annual_production (float): Average annual production of a field in the region
        
    Returns:
        float: Additional annual production of fields estimated to be explored
    """
    if fields_discovered <= 0:
        raise ValueError("Fields discovered must be positive")
    
    return (additional_fields_estimated / fields_discovered) * average_annual_production


def annual_gross_revenue_after_taxes(
    unit_price_after_taxes: float,
    annual_oil_production: float
) -> float:
    """
    Calculate annual gross revenue after royalties and wellhead taxes.
    
    Args:
        unit_price_after_taxes (float): Average unit crude price after royalties and wellhead taxes ($/bbl)
        annual_oil_production (float): Annual oil production (bbl)
        
    Returns:
        float: Annual gross revenue after royalties and wellhead taxes ($)
    """
    if unit_price_after_taxes < 0 or annual_oil_production < 0:
        raise ValueError("Price and production must be non-negative")
    
    return unit_price_after_taxes * annual_oil_production


def annuity_from_future_value(
    future_value: float,
    effective_interest_rate: float,
    time_years: float
) -> float:
    """
    Calculate annuity from future value.
    
    Args:
        future_value (float): Future value (currency unit)
        effective_interest_rate (float): Effective interest or discount rate (fraction)
        time_years (float): Time (years)
        
    Returns:
        float: Annuity from future value (currency unit)
    """
    if effective_interest_rate <= 0:
        raise ValueError("Interest rate must be positive")
    if time_years <= 0:
        raise ValueError("Time must be positive")
    
    return future_value * (effective_interest_rate / ((1 + effective_interest_rate)**time_years - 1))


def annuity_from_present_value(
    present_value: float,
    effective_interest_rate: float,
    time_years: float
) -> float:
    """
    Calculate annuity from present value.
    
    Args:
        present_value (float): Present value (currency unit)
        effective_interest_rate (float): Effective interest or discount rate (fraction)
        time_years (float): Time (years)
        
    Returns:
        float: Annuity from present value (currency unit)
    """
    if effective_interest_rate <= 0:
        raise ValueError("Interest rate must be positive")
    if time_years <= 0:
        raise ValueError("Time must be positive")
    
    numerator = effective_interest_rate * (1 + effective_interest_rate)**time_years
    denominator = (1 + effective_interest_rate)**time_years - 1
    
    return present_value * (numerator / denominator)


def effective_interest_rate_periodic_compounding(
    nominal_interest_rate: float,
    compounding_periods_per_year: int
) -> float:
    """
    Calculate effective interest rate for periodic compounding.
    
    Args:
        nominal_interest_rate (float): Nominal interest rate (fraction)
        compounding_periods_per_year (int): Number of compounding periods per year
        
    Returns:
        float: Effective interest rate (fraction)
    """
    if nominal_interest_rate < 0:
        raise ValueError("Interest rate must be non-negative")
    if compounding_periods_per_year <= 0:
        raise ValueError("Compounding periods must be positive")
    
    return (1 + nominal_interest_rate / compounding_periods_per_year)**compounding_periods_per_year - 1


def future_value_of_annuity(
    annuity: float,
    effective_interest_rate: float,
    time_years: float
) -> float:
    """
    Calculate future value of an annuity.
    
    Args:
        annuity (float): Annuity (currency unit)
        effective_interest_rate (float): Effective interest or discount rate (fraction)
        time_years (float): Time (years)
        
    Returns:
        float: Future value of annuity (currency unit)
    """
    if effective_interest_rate <= 0:
        raise ValueError("Interest rate must be positive")
    if time_years <= 0:
        raise ValueError("Time must be positive")
    
    return annuity * (((1 + effective_interest_rate)**time_years - 1) / effective_interest_rate)


def future_value_of_present_sum(
    present_value: float,
    effective_interest_rate: float,
    time_years: float
) -> float:
    """
    Calculate future value of present sum.
    
    Args:
        present_value (float): Present value (currency unit)
        effective_interest_rate (float): Effective interest or discount rate (fraction)
        time_years (float): Time (years)
        
    Returns:
        float: Future sum received at time t (currency unit)
    """
    if effective_interest_rate < 0:
        raise ValueError("Interest rate must be non-negative")
    if time_years < 0:
        raise ValueError("Time must be non-negative")
    
    return present_value * (1 + effective_interest_rate)**time_years


def generalized_expected_value(
    probabilities: List[float],
    values: List[float]
) -> float:
    """
    Calculate generalized expected value.
    
    Args:
        probabilities (List[float]): Possible results of probability from case 1 to n (fraction)
        values (List[float]): Contingency values of investment from case 1 to n ($)
        
    Returns:
        float: Expected value (dimensionless)
    """
    if len(probabilities) != len(values):
        raise ValueError("Probability and value arrays must have the same length")
    
    if not all(0 <= p <= 1 for p in probabilities):
        raise ValueError("All probabilities must be between 0 and 1")
    
    return sum(p * v for p, v in zip(probabilities, values))


def growth_rate_of_return_continuous_compounding(
    time_years: float,
    profitability_index: float,
    reinvestment_rate: float
) -> float:
    """
    Calculate growth rate of return for continuous compounding.
    
    Args:
        time_years (float): Time (years)
        profitability_index (float): Profitability index (dimensionless)
        reinvestment_rate (float): Reinvestment rate (fraction)
        
    Returns:
        float: Growth rate of return (fraction)
    """
    if time_years <= 0:
        raise ValueError("Time must be positive")
    if profitability_index <= 0:
        raise ValueError("Profitability index must be positive")
    if reinvestment_rate < 0:
        raise ValueError("Reinvestment rate must be non-negative")
    
    return (1 / time_years) * math.log(profitability_index) + reinvestment_rate


def unknown_interest_rate(
    future_amount: float,
    principal: float,
    time_years: float
) -> float:
    """
    Calculate unknown interest rate.
    
    Args:
        future_amount (float): Amount to be paid after end of t years (currency unit)
        principal (float): Amount borrowed (currency unit)
        time_years (float): Time at which F needs to be paid (years)
        
    Returns:
        float: Interest rate (fraction)
    """
    if future_amount <= 0 or principal <= 0:
        raise ValueError("Future amount and principal must be positive")
    if time_years <= 0:
        raise ValueError("Time must be positive")
    if future_amount <= principal:
        raise ValueError("Future amount must be greater than principal")
    
    return math.exp(math.log(future_amount / principal) / time_years) - 1
