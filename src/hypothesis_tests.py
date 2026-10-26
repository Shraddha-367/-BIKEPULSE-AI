"""
T20 + T21 + T22 + T23 + T24 + T25 + T26 + T27 — Hypothesis Tests
==================================================================
One-sample t, two-sample Welch t, paired t, one-way ANOVA, chi-square.
All tests show H0/H1, statistic, p-value, alpha, decision and caveats.
"""

import logging
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats
from typing import Any

logger = logging.getLogger(__name__)

ALPHA_DEFAULT = 0.05


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _decision(p_value: float, alpha: float) -> str:
    if p_value < alpha:
        return f"REJECT H0 (p={p_value:.4f} < α={alpha})"
    return f"FAIL TO REJECT H0 (p={p_value:.4f} ≥ α={alpha})"


# ---------------------------------------------------------------------------
# T20 + T21 + T22 — Hypothesis Test Framework
# ---------------------------------------------------------------------------
def hypothesis_test_meta(test_name: str, h0: str, h1: str,
                          statistic: float, p_value: float,
                          alpha: float = ALPHA_DEFAULT,
                          caveats: str = "") -> dict[str, Any]:
    """Return a standardised hypothesis test result dict (T20, T21, T22)."""
    return {
        "test": test_name,
        "H0": h0,
        "H1": h1,
        "statistic": float(statistic),
        "p_value": float(p_value),
        "alpha": alpha,
        "decision": _decision(p_value, alpha),
        "significant": bool(p_value < alpha),
        "caveats": caveats,
    }


# ---------------------------------------------------------------------------
# T23 — One-Sample T-Test
# ---------------------------------------------------------------------------
def one_sample_ttest(df: pd.DataFrame, col: str = "cnt",
                     filter_hour: int | None = None,
                     popmean: float = 189.5,
                     alpha: float = ALPHA_DEFAULT) -> dict:
    """
    One-sample t-test comparing a demand subset to a planning benchmark (T23).

    Parameters
    ----------
    filter_hour : int | None  If provided, test only that hour's demand.
    popmean : float  Planning benchmark (e.g. capacity target).
    """
    subset = df[col].dropna()
    hour_desc = "all hours"
    if filter_hour is not None:
        subset = df.loc[df["hr"] == filter_hour, col].dropna()
        hour_desc = f"hour {filter_hour}:00"

    if len(subset) < 5:
        return {"error": f"Too few observations for {hour_desc}."}

    stat, p = scipy_stats.ttest_1samp(subset, popmean=popmean)
    return hypothesis_test_meta(
        test_name="One-Sample T-Test",
        h0=f"μ (mean demand at {hour_desc}) = {popmean:.1f} rentals/hr",
        h1=f"μ (mean demand at {hour_desc}) ≠ {popmean:.1f} rentals/hr",
        statistic=stat,
        p_value=p,
        alpha=alpha,
        caveats=(
            "Assumes roughly normal distribution for the sample subset. "
            "The planning benchmark should be externally motivated (e.g. capacity, budget)."
        ),
    ) | {
        "sample_mean": float(subset.mean()),
        "sample_n": len(subset),
        "benchmark": popmean,
        "hour_filter": filter_hour,
    }


# ---------------------------------------------------------------------------
# T24 — Independent Two-Sample T-Test (Welch)
# ---------------------------------------------------------------------------
def two_sample_ttest(df: pd.DataFrame, col: str = "cnt",
                     group_col: str = "workingday",
                     group_a: int = 1, group_b: int = 0,
                     alpha: float = ALPHA_DEFAULT) -> dict:
    """
    Welch two-sample t-test: working vs non-working day demand (T24).
    Welch is preferred as group variances differ.
    """
    a = df.loc[df[group_col] == group_a, col].dropna()
    b = df.loc[df[group_col] == group_b, col].dropna()

    if len(a) < 5 or len(b) < 5:
        return {"error": "Insufficient observations for one or both groups."}

    stat, p = scipy_stats.ttest_ind(a, b, equal_var=False)
    return hypothesis_test_meta(
        test_name="Welch Two-Sample T-Test",
        h0=f"μ(workingday={group_a}) = μ(workingday={group_b})",
        h1=f"μ(workingday={group_a}) ≠ μ(workingday={group_b})",
        statistic=stat,
        p_value=p,
        alpha=alpha,
        caveats=(
            "Welch t-test does not assume equal variances. "
            "Hours within the same day are correlated — strict independence is violated. "
            "Result indicates association, not strict experimental causation."
        ),
    ) | {
        "group_a_mean": float(a.mean()),
        "group_b_mean": float(b.mean()),
        "group_a_n": len(a),
        "group_b_n": len(b),
        "group_a_label": f"workingday={group_a}",
        "group_b_label": f"workingday={group_b}",
    }


# ---------------------------------------------------------------------------
# T25 — Paired T-Test (Morning vs Evening same date)
# ---------------------------------------------------------------------------
def paired_ttest(df: pd.DataFrame, col: str = "cnt",
                 morning_hr: int = 8, evening_hr: int = 17,
                 alpha: float = ALPHA_DEFAULT) -> dict:
    """
    Paired t-test: same-date morning vs evening rush-hour demand (T25).
    Data aligned by date to ensure correct pairing.
    """
    morning = (
        df[df["hr"] == morning_hr][["dteday", col]]
        .rename(columns={col: "morning"})
        .set_index("dteday")
    )
    evening = (
        df[df["hr"] == evening_hr][["dteday", col]]
        .rename(columns={col: "evening"})
        .set_index("dteday")
    )
    paired = morning.join(evening, how="inner").dropna()

    if len(paired) < 5:
        return {"error": "Too few matched pairs."}

    stat, p = scipy_stats.ttest_rel(paired["morning"], paired["evening"])
    return hypothesis_test_meta(
        test_name="Paired T-Test (Morning vs Evening)",
        h0=f"μ(difference: morning hr={morning_hr} – evening hr={evening_hr}) = 0",
        h1=f"μ(difference: morning hr={morning_hr} – evening hr={evening_hr}) ≠ 0",
        statistic=stat,
        p_value=p,
        alpha=alpha,
        caveats=(
            "Pairs aligned on date. Assumes differences are approximately normally distributed. "
            "Temporal dependency within each day is reduced by pairing."
        ),
    ) | {
        "n_pairs": len(paired),
        "mean_morning": float(paired["morning"].mean()),
        "mean_evening": float(paired["evening"].mean()),
        "mean_difference": float((paired["morning"] - paired["evening"]).mean()),
    }


# ---------------------------------------------------------------------------
# T26 — One-Way ANOVA (Four Seasons)
# ---------------------------------------------------------------------------
def one_way_anova(df: pd.DataFrame, col: str = "cnt",
                  group_col: str = "season",
                  alpha: float = ALPHA_DEFAULT) -> dict:
    """
    One-way ANOVA comparing demand across four seasons (T26).
    Includes basic assumption diagnostics.
    """
    groups = []
    group_labels = []
    group_stats = {}
    for season_id in sorted(df[group_col].unique()):
        g = df.loc[df[group_col] == season_id, col].dropna()
        groups.append(g)
        label = str(season_id)
        group_labels.append(label)
        group_stats[label] = {
            "n": len(g),
            "mean": round(float(g.mean()), 2),
            "std": round(float(g.std(ddof=1)), 2),
        }

    if len(groups) < 2 or any(len(g) < 2 for g in groups):
        return {"error": "Insufficient data for ANOVA."}

    stat, p = scipy_stats.f_oneway(*groups)

    # Levene test for homogeneity of variance
    lev_stat, lev_p = scipy_stats.levene(*groups)

    return hypothesis_test_meta(
        test_name="One-Way ANOVA (Seasonal Demand)",
        h0=f"All season group means of {col} are equal.",
        h1="At least one season group mean differs.",
        statistic=stat,
        p_value=p,
        alpha=alpha,
        caveats=(
            "ANOVA assumes homogeneity of variances and approximate normality. "
            f"Levene's test for equal variances: F={lev_stat:.3f}, p={lev_p:.4f}. "
            "If Levene p<0.05, consider Welch ANOVA or Kruskal-Wallis non-parametric test."
        ),
    ) | {
        "groups": group_stats,
        "levene_stat": float(lev_stat),
        "levene_p": float(lev_p),
        "n_groups": len(groups),
    }


# ---------------------------------------------------------------------------
# T27 — Chi-Square Test of Independence
# ---------------------------------------------------------------------------
def chi_square_independence(df: pd.DataFrame,
                             cat_col: str = "weathersit",
                             high_demand_col: str = "high_demand",
                             alpha: float = ALPHA_DEFAULT) -> dict:
    """
    Chi-square test: weather situation vs high-demand label (T27).
    Uses training-derived high_demand label if present; else derives on spot.
    Validates expected cell counts (< 5 warnings per Cochran's rule).
    """
    if high_demand_col not in df.columns:
        return {"error": f"Column '{high_demand_col}' not found. Run feature engineering first."}

    ct = pd.crosstab(df[cat_col], df[high_demand_col])
    chi2, p, dof, expected = scipy_stats.chi2_contingency(ct)

    # Validate expected count rule (Cochran: all expected ≥ 5)
    low_expected = int((expected < 5).sum())
    cells_below_5 = [(int(r), int(c), round(float(expected[r, c]), 2))
                     for r in range(expected.shape[0])
                     for c in range(expected.shape[1])
                     if expected[r, c] < 5]

    return hypothesis_test_meta(
        test_name="Chi-Square Test of Independence",
        h0=f"Weather situation ({cat_col}) and high demand ({high_demand_col}) are independent.",
        h1=f"Weather situation and high demand are associated.",
        statistic=chi2,
        p_value=p,
        alpha=alpha,
        caveats=(
            f"Degrees of freedom: {dof}. "
            f"{low_expected} expected cell(s) below 5 — "
            "Cochran's rule violated if any. Consider collapsing rare weather categories. "
            "Chi-square is asymptotic; Fisher's exact test preferred for small tables."
        ),
    ) | {
        "contingency_table": ct.to_dict(),
        "expected_counts": expected.tolist(),
        "dof": int(dof),
        "cells_below_5": cells_below_5,
        "n": int(ct.values.sum()),
    }
