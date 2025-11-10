"""
Nelson-Siegel-Svensson (NSS) yield curve model.
"""
"""
Nelson–Siegel–Svensson (NSS) Yield Curve Model
----------------------------------------------

Fits the NSS model to a set of observed yields.

NSS Equation:

 y(t) = β0
        + β1 * ( (1 - exp(-t/τ1)) / (t/τ1) )
        + β2 * ( ( (1 - exp(-t/τ1)) / (t/τ1) ) - exp(-t/τ1) )
        + β3 * ( ( (1 - exp(-t/τ2)) / (t/τ2) ) - exp(-t/τ2) )

where:
 - t is maturity in YEARS
 - β0 = long-term level
 - β1 = short-term slope
 - β2 = medium-term curvature
 - β3 = additional curvature factor
 - τ1, τ2 = decay parameters

Example:
    from loader.fred_loader import get_yield_curve
    from models.nss import NSSYieldCurve

    curve = get_yield_curve()
    model = NSSYieldCurve.fit(curve)

    print(model(5))  # yield at 5Y
"""

import numpy as np
from scipy.optimize import curve_fit


# -----------------------------
# Helpers
# -----------------------------
def _maturity_to_years(tag: str) -> float:
    tag = tag.upper().strip()
    if tag.endswith("M"):
        return float(tag[:-1]) / 12.0
    elif tag.endswith("Y"):
        return float(tag[:-1])
    raise ValueError(f"Unknown maturity tag: {tag}")


# -----------------------------
# NSS Equation
# -----------------------------
def nss_formula(t, beta0, beta1, beta2, beta3, tau1, tau2):
    t = np.asarray(t, dtype=float)

    # Avoid division by zero for very small t
    t = np.where(t == 0, 1e-6, t)

    term1 = (1 - np.exp(-t / tau1)) / (t / tau1)
    term2 = term1 - np.exp(-t / tau1)

    term3 = (1 - np.exp(-t / tau2)) / (t / tau2)
    term4 = term3 - np.exp(-t / tau2)

    return beta0 + beta1 * term1 + beta2 * term2 + beta3 * term4


# -----------------------------
# NSS Model Class
# -----------------------------
class NSSYieldCurve:
    """
    Fits and evaluates the Nelson–Siegel–Svensson yield curve model.

    Usage:
        model = NSSYieldCurve.fit(curve_dict)
        model(2.5)  # return the yield at 2.5 years
    """

    def __init__(self, params):
        """
        params: (beta0, beta1, beta2, beta3, tau1, tau2)
        """
        self.beta0, self.beta1, self.beta2, self.beta3, self.tau1, self.tau2 = params

    # ---------------------------------------------------------
    # Model evaluation
    # ---------------------------------------------------------
    def __call__(self, t):
        return nss_formula(t, self.beta0, self.beta1, self.beta2, self.beta3, self.tau1, self.tau2)

    # ---------------------------------------------------------
    # Fit NSS from dictionary
    # ---------------------------------------------------------
    @classmethod
    def fit(cls, curve_dict):
        """
        curve_dict: {'1M': 4.1, '3M': 4.03, '1Y': 3.77, ..., '30Y': 4.11}

        Returns: NSSYieldCurve instance
        """
        maturities = np.array([_maturity_to_years(k) for k in curve_dict.keys()])
        yields = np.array([float(v) for v in curve_dict.values()])

        # Sort by maturity
        idx = np.argsort(maturities)
        x = maturities[idx]
        y = yields[idx]

        # Initial parameter guess (important for convergence)
        start_params = [
            y[-1],        # beta0: long-term level
            y[0] - y[-1], # beta1: slope
            -1.0,         # beta2: curvature
            1.0,          # beta3: curvature 2
            1.0,          # tau1
            3.0           # tau2
        ]

        # Parameter bounds (keeps optimizer stable)
        bounds = (
            [-10, -20, -20, -20, 0.01, 0.01],
            [20, 20, 20, 20, 50, 50]
        )

        # Fit parameters
        params, _ = curve_fit(
            nss_formula,
            x,
            y,
            p0=start_params,
            bounds=bounds,
            maxfev=20000
        )

        return cls(params)

    # ---------------------------------------------------------
    # Utility: Produce smooth curve for plotting
    # ---------------------------------------------------------
    def generate_curve(self, min_t=0.0, max_t=30.0, num=300):
        xs = np.linspace(min_t, max_t, num)
        ys = self(xs)
        return xs, ys

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------
    def summary(self):
        print("📘 Nelson–Siegel–Svensson Model Parameters:")
        print(f"  β0  (level):     {self.beta0:.6f}")
        print(f"  β1  (slope):     {self.beta1:.6f}")
        print(f"  β2  (curvature1):{self.beta2:.6f}")
        print(f"  β3  (curvature2):{self.beta3:.6f}")
        print(f"  τ1  (decay1):    {self.tau1:.6f}")
        print(f"  τ2  (decay2):    {self.tau2:.6f}")


