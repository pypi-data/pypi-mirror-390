"""
Plotting utilities for yield curves.
"""

"""
Plotting Utilities for Yield Curve Models
-----------------------------------------

Supports:
 - Raw observed yield points
 - CubicSplineYieldCurve (models/spline.py)
 - NSSYieldCurve (models/nss.py)

Example:
    from loader.fred_loader import get_yield_curve
    from models.spline import CubicSplineYieldCurve
    from models.nss import NSSYieldCurve
    from plots.plot_curve import plot_yield_curves

    curve = get_yield_curve()
    spline = CubicSplineYieldCurve(curve)
    nss = NSSYieldCurve.fit(curve)

    plot_yield_curves(curve, spline_model=spline, nss_model=nss)
"""

import numpy as np
import matplotlib.pyplot as plt


# -----------------------------
# Helper: convert '1M', '2Y', etc. → years
# -----------------------------
def _maturity_to_years(tag: str) -> float:
    tag = tag.upper().strip()
    if tag.endswith("M"):
        return float(tag[:-1]) / 12.0
    elif tag.endswith("Y"):
        return float(tag[:-1])
    else:
        raise ValueError(f"Unknown maturity format: {tag}")


# -----------------------------
# Plot raw points + optional models
# -----------------------------
def plot_yield_curves(
    curve_dict,
    spline_model=None,
    nss_model=None,
    title="Yield Curve Models",
    save_path=None,
    show=True,
    num_points=300
):
    """
    curve_dict: observed yields, e.g. {'1M': 4.0, '3M': 3.9, '1Y': 3.5, ...}
    spline_model: instance of CubicSplineYieldCurve
    nss_model: instance of NSSYieldCurve
    """

    # Convert maturities → years
    xs_raw = np.array([_maturity_to_years(k) for k in curve_dict.keys()])
    ys_raw = np.array([float(v) for v in curve_dict.values()])

    # Sort raw values
    idx = np.argsort(xs_raw)
    xs_raw = xs_raw[idx]
    ys_raw = ys_raw[idx]

    # Prepare figure
    plt.figure(figsize=(12, 7))

    # Plot raw observed yields
    plt.scatter(xs_raw, ys_raw, color="black", label="Observed Points", s=55, zorder=5)

    # Plot spline model
    if spline_model is not None:
        xs_spline = np.linspace(xs_raw.min(), xs_raw.max(), num_points)
        ys_spline = spline_model(xs_spline)
        plt.plot(xs_spline, ys_spline, label="Cubic Spline", linewidth=2.5, color="blue")

    # Plot NSS model
    if nss_model is not None:
        xs_nss = np.linspace(xs_raw.min(), xs_raw.max(), num_points)
        ys_nss = nss_model(xs_nss)
        plt.plot(xs_nss, ys_nss, label="NSS", linewidth=2.5, linestyle="--", color="red")

    # Labels + styles
    plt.title(title, fontsize=16, fontweight="bold")
    plt.xlabel("Maturity (Years)", fontsize=14)
    plt.ylabel("Yield (%)", fontsize=14)

    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=13)
    plt.tight_layout()

    # Save to file
    if save_path is not None:
        plt.savefig(save_path, dpi=300)

    # Show
    if show:
        plt.show()

    return True

