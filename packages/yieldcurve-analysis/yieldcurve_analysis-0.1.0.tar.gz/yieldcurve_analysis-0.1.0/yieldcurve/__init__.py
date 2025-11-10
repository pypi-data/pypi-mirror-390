"""
Yield Curve Analysis Package
----------------------------

A Python package for downloading US Treasury yields from FRED, fitting
Cubic Spline and Nelson–Siegel–Svensson models, and visualizing the curve.
"""

__version__ = "0.1.0"

# Public API
from .loader.fred_loader import get_yield_curve
from .models.spline import CubicSplineYieldCurve
from .models.nss import NSSYieldCurve
from .plots.plot_curve import plot_yield_curves

# Convenience functions
def fit_spline(curve_dict):
    """
    Fit a cubic spline model to a yield curve.
    
    Args:
        curve_dict: Dictionary mapping maturity labels to yields
    
    Returns:
        CubicSplineYieldCurve: Fitted spline model
    
    Example:
        >>> from yieldcurve import get_yield_curve, fit_spline
        >>> curve = get_yield_curve()
        >>> model = fit_spline(curve)
    """
    return CubicSplineYieldCurve(curve_dict)


def fit_nss(curve_dict):
    """
    Fit a Nelson–Siegel–Svensson model to a yield curve.
    
    Args:
        curve_dict: Dictionary mapping maturity labels to yields
    
    Returns:
        NSSYieldCurve: Fitted NSS model
    
    Example:
        >>> from yieldcurve import get_yield_curve, fit_nss
        >>> curve = get_yield_curve()
        >>> model = fit_nss(curve)
    """
    return NSSYieldCurve.fit(curve_dict)


def load_yields():
    """
    Alias for get_yield_curve() for convenience.
    
    Returns:
        dict: Dictionary mapping maturity labels to yields
    
    Example:
        >>> from yieldcurve import load_yields
        >>> curve = load_yields()
    """
    return get_yield_curve()


__all__ = [
    "get_yield_curve",
    "load_yields",
    "CubicSplineYieldCurve",
    "NSSYieldCurve",
    "fit_spline",
    "fit_nss",
    "plot_yield_curves",
]

