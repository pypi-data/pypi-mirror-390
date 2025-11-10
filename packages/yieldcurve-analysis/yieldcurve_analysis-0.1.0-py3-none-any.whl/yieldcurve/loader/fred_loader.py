"""
FRED (Federal Reserve Economic Data) loader for yield curve data.
"""
import requests
import csv
from io import StringIO

# -----------------------------
# MATURITY CONVERSION TABLE
# -----------------------------
MATURITY_MAP = {
    "1M": 1/12,
    "3M": 3/12,
    "6M": 6/12,
    "1Y": 1,
    "2Y": 2,
    "3Y": 3,
    "5Y": 5,
    "7Y": 7,
    "10Y": 10,
    "20Y": 20,
    "30Y": 30
}

# -----------------------------
# FRED SERIES IDS (H.15 data)
# -----------------------------
FRED_SERIES = {
    "1M": "DGS1MO",
    "3M": "DGS3MO",
    "6M": "DGS6MO",
    "1Y": "DGS1",
    "2Y": "DGS2",
    "3Y": "DGS3",
    "5Y": "DGS5",
    "7Y": "DGS7",
    "10Y": "DGS10",
    "20Y": "DGS20",
    "30Y": "DGS30"
}

# -----------------------------
# FETCH FROM FRED (CSV, NO API KEY)
# -----------------------------
def fetch_from_fred():
    print("Fetching U.S. Treasury yield curve via FRED (no API key)...\n")

    curve = {}

    for label, series_id in FRED_SERIES.items():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        r = requests.get(url)

        if r.status_code != 200:
            continue

        csv_data = list(csv.reader(StringIO(r.text)))
        if len(csv_data) < 2:
            continue

        # Last valid row (skips blanks)
        last_val = csv_data[-1][1]
        try:
            curve[label] = float(last_val)
        except:
            continue

    # Sort maturities in ascending order
    curve = dict(sorted(curve.items(), key=lambda x: MATURITY_MAP[x[0]]))
    return curve

# -----------------------------
# MAIN USER FUNCTION
# -----------------------------
def get_yield_curve():
    """
    Fetch the current U.S. Treasury yield curve from FRED.
    
    Returns:
        dict: Dictionary mapping maturity labels to yields (e.g., {'1M': 4.02, '3M': 3.93, ...})
              Sorted by maturity in ascending order.
    
    Example:
        >>> curve = get_yield_curve()
        >>> print(curve['10Y'])
        4.11
    """
    return fetch_from_fred()


