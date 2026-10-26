"""
T07 — Descriptive Statistics
============================
Functions for computing mean, median, mode, range, variance,
standard deviation, quartiles and IQR on any numeric Series or DataFrame.
All computations use genuine data values only.
"""

import logging
from typing import Any
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

logger = logging.getLogger(__name__)


def compute_descriptive_stats(series: pd.Series) -> dict[str, Any]:
    """
    Compute full descriptive statistics for a numeric Series (T07).

    Parameters
    ----------
    series : pd.Series
        Numeric series (e.g. df['cnt']).

    Returns
    -------
    dict
        Keys: count, mean, median, mode, std, variance, range,
              min, max, q1, q3, iqr, skewness, kurtosis.
    """
    s = series.dropna()
    if s.empty:
        return {}

    mode_result = scipy_stats.mode(s.values, keepdims=True)
    mode_val = float(mode_result.mode[0]) if len(mode_result.mode) > 0 else float("nan")
    mode_count = int(mode_result.count[0]) if len(mode_result.count) > 0 else 0

    q1 = float(np.percentile(s, 25))
    q3 = float(np.percentile(s, 75))

    return {
        "count": int(s.count()),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "mode": mode_val,
        "mode_count": mode_count,
        "std": float(s.std(ddof=1)),
        "variance": float(s.var(ddof=1)),
        "range": float(s.max() - s.min()),
        "min": float(s.min()),
        "max": float(s.max()),
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
        "skewness": float(s.skew()),
        "kurtosis": float(s.kurtosis()),
    }


def compute_grouped_stats(df: pd.DataFrame, group_col: str,
                          value_col: str = "cnt") -> pd.DataFrame:
    """
    Compute descriptive stats grouped by a categorical column.

    Parameters
    ----------
    df : pd.DataFrame
    group_col : str
        Grouping column (e.g. 'season', 'hr', 'weathersit').
    value_col : str
        Numeric column to aggregate.

    Returns
    -------
    pd.DataFrame
        DataFrame with group, count, mean, median, std, min, max, q1, q3, iqr.
    """
    results = []
    for group, grp in df.groupby(group_col):
        s = grp[value_col]
        q1 = float(np.percentile(s, 25))
        q3 = float(np.percentile(s, 75))
        results.append(
            {
                group_col: group,
                "count": len(s),
                "mean": round(s.mean(), 2),
                "median": round(s.median(), 2),
                "std": round(s.std(ddof=1), 2),
                "min": int(s.min()),
                "max": int(s.max()),
                "q1": round(q1, 2),
                "q3": round(q3, 2),
                "iqr": round(q3 - q1, 2),
            }
        )
    return pd.DataFrame(results)


def summarise_dataframe(df: pd.DataFrame,
                        cols: list[str] | None = None) -> pd.DataFrame:
    """
    Compute descriptive stats for multiple columns.

    Parameters
    ----------
    df : pd.DataFrame
    cols : list[str] | None
        Columns to summarise. If None, uses all numeric columns.

    Returns
    -------
    pd.DataFrame
        Wide table with statistics as rows and columns as columns.
    """
    if cols is None:
        cols = df.select_dtypes(include=[np.number]).columns.tolist()

    rows = {}
    for col in cols:
        rows[col] = compute_descriptive_stats(df[col])
    return pd.DataFrame(rows).T
