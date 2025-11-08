"""
petrocalc: A comprehensive Python library for petroleum engineering calculations.

This library provides modules for various petroleum engineering calculations including:
- Drilling and wellbore calculations
- Reservoir engineering
- Production engineering  
- Fluid properties
- Rock properties
- Well completion and stimulation
- Enhanced oil recovery and geothermal
- Facilities and process engineering
- And more...

Author: Muhammad Farzad Ali
"""

__version__ = "1.2.1"
__author__ = "Muhammad Farzad Ali"
__email__ = "muhammad.farzad.ali@gmail.com"

# Import main modules for easy access
from . import drilling
from . import reservoir
from . import production
from . import fluids
from . import rock_properties
from . import completion
from . import pressure
from . import flow
from . import thermodynamics
from . import economics
from . import gas_reservoir
from . import well_testing
from . import petrophysics
from . import geomechanics
from . import laboratory
from . import enhanced_recovery
from . import facilities

__all__ = [
    "drilling",
    "reservoir", 
    "production",
    "fluids",
    "rock_properties",
    "completion",
    "pressure",
    "flow", 
    "thermodynamics",
    "economics",
    "gas_reservoir",
    "well_testing",
    "petrophysics",
    "geomechanics",
    "laboratory",
    "enhanced_recovery",
    "facilities"
]
