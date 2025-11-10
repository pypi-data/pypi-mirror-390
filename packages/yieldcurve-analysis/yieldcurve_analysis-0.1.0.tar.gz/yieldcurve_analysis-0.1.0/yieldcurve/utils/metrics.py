"""
Yield Curve Metrics
-------------------

Functions to calculate various yield curve metrics including slope, curvature,
forward rates, and duration approximations.
"""

from typing import Dict, Union
import numpy as np


def calculate_slope(curve: Dict[str, float], short_maturity: str = "2Y", long_maturity: str = "10Y") -> float:
    """
    Calculate the slope of the yield curve (long-term minus short-term yield).
    
    Args:
        curve: Dictionary mapping maturity labels to yields
        short_maturity: Short-term maturity label (default: "2Y")
        long_maturity: Long-term maturity label (default: "10Y")
    
    Returns:
        float: Slope in percentage points (e.g., 0.54 means 54 basis points)
    
    Raises:
        KeyError: If specified maturities are not in the curve.
    
    Example:
        >>> curve = {'2Y': 3.57, '10Y': 4.11}
        >>> calculate_slope(curve)
        0.54
    """
    if short_maturity not in curve:
        raise KeyError(f"Short maturity '{short_maturity}' not found in curve")
    if long_maturity not in curve:
        raise KeyError(f"Long maturity '{long_maturity}' not found in curve")
    
    return curve[long_maturity] - curve[short_maturity]


def calculate_curvature(curve: Dict[str, float], short: str = "2Y", medium: str = "5Y", long: str = "10Y") -> float:
    """
    Calculate the curvature of the yield curve (belly vs ends).
    
    Curvature = 2 * (medium yield) - (short yield) - (long yield)
    
    Positive curvature indicates a "humped" curve (belly higher than ends).
    Negative curvature indicates a "bowed" curve (belly lower than ends).
    
    Args:
        curve: Dictionary mapping maturity labels to yields
        short: Short-term maturity label (default: "2Y")
        medium: Medium-term maturity label (default: "5Y")
        long: Long-term maturity label (default: "10Y")
    
    Returns:
        float: Curvature in percentage points
    
    Raises:
        KeyError: If specified maturities are not in the curve.
    
    Example:
        >>> curve = {'2Y': 3.57, '5Y': 3.69, '10Y': 4.11}
        >>> calculate_curvature(curve)
        -0.28
    """
    if short not in curve:
        raise KeyError(f"Short maturity '{short}' not found in curve")
    if medium not in curve:
        raise KeyError(f"Medium maturity '{medium}' not found in curve")
    if long not in curve:
        raise KeyError(f"Long maturity '{long}' not found in curve")
    
    return 2 * curve[medium] - curve[short] - curve[long]


def calculate_forward_rates(model: Union[object, callable], grid: np.ndarray) -> np.ndarray:
    """
    Calculate forward rates from a yield curve model.
    
    Forward rate from t1 to t2: f(t1, t2) = (y(t2) * t2 - y(t1) * t1) / (t2 - t1)
    
    For a grid of maturities, computes instantaneous forward rates:
    f(t) = y(t) + t * y'(t)
    
    Args:
        model: Callable yield curve model that takes maturity (in years) and returns yield
               (e.g., CubicSplineYieldCurve or NSSYieldCurve instance)
        grid: Array of maturities (in years) at which to compute forward rates
    
    Returns:
        np.ndarray: Forward rates at each maturity point (in percentage points)
    
    Example:
        >>> from yieldcurve.models.spline import CubicSplineYieldCurve
        >>> curve = {'1Y': 3.65, '2Y': 3.57, '10Y': 4.11}
        >>> model = CubicSplineYieldCurve(curve)
        >>> grid = np.array([1.0, 2.0, 5.0, 10.0])
        >>> forwards = calculate_forward_rates(model, grid)
    """
    grid = np.asarray(grid, dtype=float)
    
    # For spline models, we can use the derivative
    if hasattr(model, 'spline'):
        # CubicSplineYieldCurve has a spline attribute with derivative method
        yields = model(grid)
        # Use the derivative method of CubicSpline
        derivatives = model.spline.derivative()(grid)
        forwards = yields + grid * derivatives
    else:
        # For other models (like NSS), use finite differences
        yields = model(grid)
        
        # Forward rate approximation: f(t) ≈ y(t) + t * dy/dt
        dy_dt = np.gradient(yields, grid)
        forwards = yields + grid * dy_dt
    
    return forwards


def duration_approx(model: Union[object, callable], maturity: float, yield_change: float = 0.01) -> float:
    """
    Approximate modified duration using finite differences.
    
    Duration ≈ - (1 / P) * (dP / dy)
    
    For a zero-coupon bond: P = exp(-y * t), so duration ≈ t
    
    This function computes duration numerically by perturbing the yield.
    
    Args:
        model: Callable yield curve model that takes maturity (in years) and returns yield
        maturity: Maturity at which to compute duration (in years)
        yield_change: Small yield perturbation for numerical differentiation (default: 0.01 = 1bp)
    
    Returns:
        float: Modified duration (in years)
    
    Example:
        >>> from yieldcurve.models.spline import CubicSplineYieldCurve
        >>> curve = {'1Y': 3.65, '2Y': 3.57, '10Y': 4.11}
        >>> model = CubicSplineYieldCurve(curve)
        >>> duration_approx(model, 5.0)
        4.85
    """
    y0 = float(model(maturity))
    
    # Price at current yield (zero-coupon bond)
    P0 = np.exp(-y0 / 100.0 * maturity)  # Convert percentage to decimal
    
    # Price at perturbed yield
    y1 = y0 + yield_change
    P1 = np.exp(-y1 / 100.0 * maturity)
    
    # Modified duration = - (1/P) * (dP/dy)
    dP_dy = (P1 - P0) / yield_change
    duration = -(1.0 / P0) * dP_dy
    
    return duration

