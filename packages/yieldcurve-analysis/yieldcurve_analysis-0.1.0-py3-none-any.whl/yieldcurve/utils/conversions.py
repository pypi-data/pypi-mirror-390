"""
Maturity Conversion Utilities
-----------------------------

Helper functions for converting between maturity formats and sorting yield curves.
"""

from typing import Dict


def maturity_to_years(tag: str) -> float:
    """
    Convert maturity tag to years.
    
    Args:
        tag: Maturity string like '1M', '3M', '6M', '1Y', '2Y', '10Y', etc.
    
    Returns:
        float: Maturity in years (e.g., '3M' -> 0.25, '2Y' -> 2.0)
    
    Raises:
        ValueError: If tag format is not recognized.
    
    Example:
        >>> maturity_to_years('3M')
        0.25
        >>> maturity_to_years('10Y')
        10.0
    """
    tag = tag.upper().strip()
    if tag.endswith("M"):
        return float(tag[:-1]) / 12.0
    elif tag.endswith("Y"):
        return float(tag[:-1])
    else:
        raise ValueError(f"Unknown maturity format: {tag}. Expected format: 'XM' or 'XY' (e.g., '3M', '10Y')")


def years_to_maturity(years: float) -> str:
    """
    Convert years to standard maturity tag.
    
    Args:
        years: Maturity in years (e.g., 0.25, 2.0, 10.0)
    
    Returns:
        str: Maturity tag (e.g., 0.25 -> '3M', 2.0 -> '2Y')
    
    Example:
        >>> years_to_maturity(0.25)
        '3M'
        >>> years_to_maturity(2.0)
        '2Y'
        >>> years_to_maturity(0.0833)
        '1M'
    """
    if years < 1.0:
        months = round(years * 12)
        if months == 1:
            return "1M"
        elif months == 3:
            return "3M"
        elif months == 6:
            return "6M"
        else:
            # For non-standard months, return as-is
            return f"{months}M"
    else:
        years_int = int(round(years))
        return f"{years_int}Y"


def sort_curve_dict(curve_dict: Dict[str, float]) -> Dict[str, float]:
    """
    Sort a yield curve dictionary by maturity in ascending order.
    
    Args:
        curve_dict: Dictionary mapping maturity labels to yields
                    (e.g., {'10Y': 4.11, '1M': 4.02, '3M': 3.93})
    
    Returns:
        dict: Sorted dictionary by maturity (e.g., {'1M': 4.02, '3M': 3.93, '10Y': 4.11})
    
    Example:
        >>> curve = {'10Y': 4.11, '1M': 4.02, '3M': 3.93}
        >>> sort_curve_dict(curve)
        {'1M': 4.02, '3M': 3.93, '10Y': 4.11}
    """
    if not isinstance(curve_dict, dict):
        raise TypeError("curve_dict must be a dictionary")
    
    return dict(sorted(curve_dict.items(), key=lambda x: maturity_to_years(x[0])))

