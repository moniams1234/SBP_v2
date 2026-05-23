"""
Historical volatility calculation from uploaded price series.
Supports CSV and XLSX. Handles Polish decimal comma format.
"""

import io
import numpy as np
import pandas as pd

FREQ_FACTORS = {"daily": 252, "weekly": 52, "monthly": 12}


def parse_polish_number(val):
    """Convert Polish decimal-comma string to float, e.g. '122,08' → 122.08."""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val = val.strip().replace("\xa0", "").replace(" ", "")
        val = val.replace(",", ".")
        try:
            return float(val)
        except ValueError:
            return np.nan
    return np.nan


def clean_series(series: pd.Series) -> pd.Series:
    """Clean a price column, handling Polish comma format."""
    return series.apply(parse_polish_number).dropna()


def compute_log_returns(prices: pd.Series) -> pd.Series:
    """Compute ln(Pt / Pt-1) log returns."""
    prices = clean_series(prices)
    if len(prices) < 2:
        raise ValueError("Need at least 2 price observations to compute returns.")
    return np.log(prices / prices.shift(1)).dropna()


def annualize_std(std: float, frequency: str) -> float:
    factor = FREQ_FACTORS.get(frequency)
    if factor is None:
        raise ValueError(f"Unknown frequency: {frequency}. Use daily/weekly/monthly.")
    return std * np.sqrt(factor)


def compute_volatility(prices: pd.Series, frequency: str = "daily"):
    """
    Full volatility pipeline.
    Returns dict with log_returns, std, ann_vol, factor.
    """
    log_returns = compute_log_returns(prices)
    std = log_returns.std(ddof=1)
    factor = np.sqrt(FREQ_FACTORS[frequency])
    ann_vol = std * factor
    return {"log_returns": log_returns, "std": std, "ann_vol": ann_vol, "factor": factor}


def load_uploaded_file(uploaded_file) -> pd.DataFrame:
    """Load CSV or XLSX uploaded file to DataFrame."""
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(io.BytesIO(raw))
    # CSV: try common separators
    for sep in [",", ";", "\t", "|"]:
        try:
            df = pd.read_csv(io.BytesIO(raw), sep=sep)
            if len(df.columns) > 1 or len(df) > 0:
                return df
        except Exception:
            continue
    return pd.read_csv(io.BytesIO(raw))
