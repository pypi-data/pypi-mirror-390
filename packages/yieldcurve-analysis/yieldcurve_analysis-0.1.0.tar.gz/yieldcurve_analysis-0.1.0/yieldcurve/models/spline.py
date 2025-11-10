"""
Cubic Spline Yield Curve Model
------------------------------

This module fits a cubic spline to a set of zero-coupon yields obtained
from the FRED loader, using maturities expressed in months or years.

Example:
    from loader.fred_loader import get_yield_curve
    from models.spline import CubicSplineYieldCurve

    curve = get_yield_curve()
    model = CubicSplineYieldCurve(curve)

    # Evaluate 2-year yield
    print(model(2.0))

    # Generate smooth curve
    xs, ys = model.generate_curve()
"""

import numpy as np
from scipy.interpolate import CubicSpline


# -----------------------------
# Helpers
# -----------------------------
def _maturity_to_years(tag: str) -> float:
    """Converts maturities like '1M', '6M', '1Y', '10Y' -> years."""
    tag = tag.upper().strip()
    if tag.endswith("M"):
        return float(tag[:-1]) / 12.0
    elif tag.endswith("Y"):
        return float(tag[:-1])
    else:
        raise ValueError(f"Unknown maturity format: {tag}")


# -----------------------------
# Cubic Spline Model
# -----------------------------
class CubicSplineYieldCurve:
    """
    Fits a cubic spline to a yield curve dictionary {maturity: rate}.

    - maturities: keys like '3M', '1Y', '10Y'
    - yields: annualized percentage yields, e.g., 4.15

    After fitting, you can evaluate yields at any positive maturity (in years):

        yc = CubicSplineYieldCurve(curve)
        yc(2.7)   # yield at 2.7 years
    """

    def __init__(self, curve_dict):
        """
        curve_dict: dict like {'1M': 4.12, '3M': 4.05, '1Y': 3.60, '10Y': 4.12}
        """
        if not isinstance(curve_dict, dict):
            raise TypeError("curve_dict must be a dict {maturity: yield}")

        # Convert maturities -> years
        maturities = np.array([_maturity_to_years(k) for k in curve_dict.keys()])
        yields = np.array([float(v) for v in curve_dict.values()])

        # Sort by increasing maturity
        order = np.argsort(maturities)
        self.x = maturities[order]
        self.y = yields[order]

        # Fit the cubic spline
        self.spline = CubicSpline(self.x, self.y, bc_type='natural')

    # ---------------------------------------------------------
    # Evaluation
    # ---------------------------------------------------------
    def __call__(self, t):
        """
        Evaluate the spline at maturity t (float or array), where t is in YEARS.
        """
        t = np.asarray(t, dtype=float)
        if np.any(t < 0):
            raise ValueError("Maturity must be >= 0")
        return self.spline(t)

    # ---------------------------------------------------------
    # Utility: generate smooth curve
    # ---------------------------------------------------------
    def generate_curve(self, num=200):
        """
        Generates a smooth curve for plotting:
            returns (xs, ys)
            xs: evenly spaced maturities between min(x) and max(x)
            ys: spline yields
        """
        xs = np.linspace(self.x.min(), self.x.max(), num)
        ys = self(xs)
        return xs, ys

    # ---------------------------------------------------------
    # Utility: print summary
    # ---------------------------------------------------------
    def summary(self):
        """
        Print the base nodes of the spline.
        """
        print("📈 CubicSplineYieldCurve Model:")
        for m, y in zip(self.x, self.y):
            print(f"  {m:.4f} years  →  {y:.4f}%")
