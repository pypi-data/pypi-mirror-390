"""
Data loaders for yield curve data.
"""

from .fred_loader import get_yield_curve, fetch_from_fred

__all__ = ["get_yield_curve", "fetch_from_fred"]

