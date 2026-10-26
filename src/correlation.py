"""
T28 + T29 + T30 + T31 + T32 — Covariance Analysis, Pearson, Spearman,
Correlation Hypothesis Testing, Correlation Matrix
"""

import logging
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# T28 — Covariance Analysis
# ---------------------------------------------------------------------------
def covariance_analysis(df: pd.DataFrame,
                         cols: list[str] | None = None) -> dict:
    """
    Compute covariance between selected numerical variables (T28).

    Parameters
    ----------
    cols : list[str] | None  Columns to compute covariance for.

    Returns
    -------
    dict with covariance_matrix and pairwise covariances.
    """
    if cols is None:
        cols = ["temp", "atemp", "hum", "windspeed", "cnt"]
    available = [c for c in cols if c in df.columns]
    cov_matrix = df[available].cov()

    pairwise = {}
    for i, c1 in enumerate(available):
        for c2 in available[i + 1:]:
            pairwise[f"{c1}–{c2}"] = {
                "covariance": round(float(cov_matrix.loc[c1, c2]), 6),
                "interpretation": _interpret_covariance(cov_matrix.loc[c1, c2]),
            }

    return {
        "columns": available,
        "covariance_matrix": cov_matrix.round(6).to_dict(),
        "pairwise": pairwise,
        "note": (
            "Covariance magnitude depends on the scale of variables. "
            "Normalized UCI variables (temp, atemp, hum, windspeed) "
            "have covariances in the range [0, 1]."
        ),
    }


def _interpret_covariance(cov: float) -> str:
    if cov > 0.01:
        return "Positive relationship"
    elif cov < -0.01:
        return "Negative relationship"
    return "Near-zero relationship"


# ---------------------------------------------------------------------------
# T29 — Pearson Correlation
# ---------------------------------------------------------------------------
def pearson_correlation(df: pd.DataFrame, col_x: str = "temp",
                         col_y: str = "cnt") -> dict:
    """
    Pearson r and significance test for two continuous variables (T29, T31).
    """
    x = df[col_x].dropna()
    y = df[col_y].dropna()
    # Align on index
    aligned = pd.concat([x, y], axis=1).dropna()
    x_a = aligned.iloc[:, 0].values
    y_a = aligned.iloc[:, 1].values

    r, p = scipy_stats.pearsonr(x_a, y_a)

    return {
        "test": "Pearson Correlation",
        "x_col": col_x,
        "y_col": col_y,
        "r": float(r),
        "p_value": float(p),
        "n": len(aligned),
        "H0": f"H0: ρ (Pearson) between {col_x} and {col_y} = 0",
        "H1": f"H1: ρ ≠ 0",
        "significant": bool(p < 0.05),
        "interpretation": _interpret_r(r),
        "assumptions": (
            "Pearson r assumes linearity, continuous data and approximate bivariate normality. "
            "Large samples (n>30) make the normality assumption less critical."
        ),
    }


def _interpret_r(r: float) -> str:
    abs_r = abs(r)
    direction = "positive" if r > 0 else "negative"
    if abs_r >= 0.7:
        strength = "strong"
    elif abs_r >= 0.4:
        strength = "moderate"
    elif abs_r >= 0.2:
        strength = "weak"
    else:
        strength = "negligible"
    return f"{strength} {direction} linear relationship"


# ---------------------------------------------------------------------------
# T30 — Spearman Rank Correlation
# ---------------------------------------------------------------------------
def spearman_correlation(df: pd.DataFrame, col_x: str = "temp",
                          col_y: str = "cnt") -> dict:
    """
    Spearman rho and significance test (T30, T31).
    """
    aligned = df[[col_x, col_y]].dropna()
    rho, p = scipy_stats.spearmanr(aligned[col_x], aligned[col_y])

    return {
        "test": "Spearman Rank Correlation",
        "x_col": col_x,
        "y_col": col_y,
        "rho": float(rho),
        "p_value": float(p),
        "n": len(aligned),
        "H0": f"H0: ρ_s (Spearman) between {col_x} and {col_y} = 0",
        "H1": "H1: ρ_s ≠ 0",
        "significant": bool(p < 0.05),
        "interpretation": _interpret_r(rho),
        "assumptions": (
            "Spearman rho is non-parametric; robust to outliers and monotone non-linear relationships. "
            "Does not require bivariate normality."
        ),
    }


# ---------------------------------------------------------------------------
# T31 — Correlation Hypothesis Testing Summary
# ---------------------------------------------------------------------------
def correlation_hypothesis_tests(df: pd.DataFrame,
                                   pairs: list[tuple[str, str]] | None = None) -> list[dict]:
    """
    Run both Pearson and Spearman tests for a set of variable pairs (T31).
    """
    if pairs is None:
        pairs = [
            ("temp", "cnt"),
            ("hum", "cnt"),
            ("windspeed", "cnt"),
            ("temp", "hum"),
            ("atemp", "cnt"),
        ]

    results = []
    for col_x, col_y in pairs:
        if col_x not in df.columns or col_y not in df.columns:
            continue
        pear = pearson_correlation(df, col_x, col_y)
        spear = spearman_correlation(df, col_x, col_y)
        results.append(
            {
                "pair": f"{col_x} vs {col_y}",
                "pearson_r": pear["r"],
                "pearson_p": pear["p_value"],
                "pearson_sig": pear["significant"],
                "spearman_rho": spear["rho"],
                "spearman_p": spear["p_value"],
                "spearman_sig": spear["significant"],
                "interpretation": pear["interpretation"],
            }
        )
    return results


# ---------------------------------------------------------------------------
# T32 — Correlation Matrix (for heatmap)
# ---------------------------------------------------------------------------
def correlation_matrix(df: pd.DataFrame,
                        cols: list[str] | None = None,
                        method: str = "pearson") -> pd.DataFrame:
    """
    Compute full correlation matrix for numeric features (T32).

    Parameters
    ----------
    method : str  "pearson" or "spearman".
    """
    if cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # Exclude leakage columns
        leakage = {"instant", "casual", "registered"}
        cols = [c for c in numeric_cols if c not in leakage]

    available = [c for c in cols if c in df.columns]
    corr = df[available].corr(method=method)
    return corr
