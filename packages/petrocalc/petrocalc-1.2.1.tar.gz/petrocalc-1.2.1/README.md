# PetroCalc

PetroCalc is a comprehensive Python library for petroleum engineering calculations. It provides modular, well-documented implementations for drilling, reservoir engineering, production, fluid properties, well testing, petrophysics, geomechanics, enhanced oil recovery, facilities engineering, and economic analysis.

## Features

- 17 modules covering core petroleum engineering disciplines.
- 800+ implemented formulas and utility functions.
- Clear API for common engineering tasks and advanced analyses.
- Examples and usage snippets for quick integration.
- Designed for scientific, engineering, and production workflows.

## Core Modules (high-level)

- `petrocalc.drilling` — Mud properties, hydraulics, wellbore engineering, cementing, pressure analysis.
- `petrocalc.reservoir` — Reservoir properties, material balance, recovery, advanced calculations.
- `petrocalc.well_testing` — Buildup and flow test analysis, dimensionless parameters, radius of investigation.
- `petrocalc.production` — IPR/PR curves, artificial lift support, fracturing, perforation, completion fluids.
- `petrocalc.flow` — Dimensionless numbers, pressure drop, Darcy-Weisbach, high-pressure gas flow.
- `petrocalc.gas_reservoir` — Gas material balance, drive mechanisms, CBM calculations, special deliverability.
- `petrocalc.thermodynamics` — Heat transfer, phase behavior, thermal properties.
- `petrocalc.economics` — NPV, IRR, cash flow, cost estimation, break-even analysis.
- `petrocalc.fluids` — Oil, gas, and water properties, formation volume factors, viscosities, density.
- `petrocalc.rock_properties` — Porosity, permeability averaging, relative permeability, resistivity models.
- `petrocalc.pressure` — Effective compressibility, hydrostatic gradients, hydrate dissociation.
- `petrocalc.facilities` — Separator design, vessel sizing, compressor energy, process utilities.

## Installation

Install from PyPI:

```bash
pip install petrocalc
```

For development:

```bash
git clone https://github.com/your-username/petrocalc.git
cd petrocalc
pip install -e .
```

## Quick start

```python
import petrocalc

# Drilling: mud weight to pressure gradient
mud_grad = petrocalc.drilling.mud_weight_to_pressure_gradient(12.0, "ppg")

# Reservoir: API gravity conversion
api = petrocalc.reservoir.api_gravity_from_specific_gravity(0.85)

# Production: Vogel IPR
oil_rate = petrocalc.production.vogel_ipr(
    reservoir_pressure=3000, bottomhole_pressure=2000, maximum_oil_rate=1000
)

# Fluids: oil compressibility
oil_comp = petrocalc.fluids.isothermal_oil_compressibility_vasquez_beggs(
    solution_gor=500, gas_gravity=0.7, oil_gravity=35, temperature=180, pressure=2500
)
```

## Usage examples

### Reservoir engineering example

```python
from petrocalc import reservoir

# API gravity conversions
api_gravity = reservoir.api_gravity_from_specific_gravity(0.85)

# Permeability averaging for heterogeneous reservoir
perms = [100, 50, 200]
heights = [10, 20, 15]
avg_perm = reservoir.average_permeability_parallel_layers(perms, heights)
```

### Production engineering example

```python
from petrocalc import production

# Gas well productivity
gas_pi = production.gas_well_productivity_index(
    flow_rate=1000, reservoir_pressure=3000, bottomhole_pressure=2000
)

# Critical rate for horizontal well using Joshi correlation
critical_rate = production.horizontal_well_critical_rate_joshi(
    oil_density=50, water_density=62.4, horizontal_permeability=100,
    vertical_permeability=10, net_pay=100, horizontal_well_length=1000, distance_to_contact=50
)
```

### Fluid properties example

```python
from petrocalc import fluids

# Oil density using Standing's correlation
oil_density = fluids.oil_density_standing(
    oil_specific_gravity=0.85, solution_gas_oil_ratio=500, gas_specific_gravity=0.7, temperature=180
)

# Water formation volume factor using McCain correlation
water_fvf = fluids.water_formation_volume_factor(temperature=180, pressure=2500, salinity=50000)
```

## Advanced calculations and utilities

- Material balance and drive analysis functions.
- Well test diagnostics and dimensionless transforms.
- Facilities and process equipment sizing utilities.
- Economic evaluation helpers: NPV, IRR, discounted cash flows.

## Recent updates

- Expanded formula coverage across modules.
- New critical rate correlations and viscosity correlations.
- Enhanced wellbore radius methods and material balance tools.
- Additional examples and improved documentation.

## Contributing

- Contributions, bug reports, and feature requests are welcome via the repository.
- Follow repository contribution guidelines and tests for pull requests.

## License

- See LICENSE file for terms.

## Contact

- For questions or commercial support, open an issue or contact the repository maintainers.
