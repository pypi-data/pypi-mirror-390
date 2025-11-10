"""
Utility functions for yield curve analysis.
"""

from .conversions import maturity_to_years, years_to_maturity, sort_curve_dict
from .metrics import (
    calculate_slope,
    calculate_curvature,
    calculate_forward_rates,
    duration_approx
)

__all__ = [
    "maturity_to_years",
    "years_to_maturity",
    "sort_curve_dict",
    "calculate_slope",
    "calculate_curvature",
    "calculate_forward_rates",
    "duration_approx",
]

