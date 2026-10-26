"""
T14 + T15 + T16 + T17 + T18 + T19 — Statistical Inference
===========================================================
Point estimation, standard error, bootstrap, confidence intervals,
coverage probability simulation, and mean vs. median comparison.
All using genuine data; synthetic simulations clearly labelled.
"""

import logging
import warnings
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# T14 — Point Estimation
# ---------------------------------------------------------------------------
def point_estimates(series: pd.Series,
                    high_demand_threshold: float | None = None) -> dict:
    """
    Compute point estimates for mean, median and high-demand proportion (T14).

    Parameters
    ----------
    series : pd.Series  Numeric hourly rental count.
    high_demand_threshold : float | None  75th-percentile based threshold.

    Returns
    -------
    dict with mean_estimate, median_estimate, proportion_high_demand, threshold.
    """
    s = series.dropna()
    if high_demand_threshold is None:
        high_demand_threshold = float(np.percentile(s, 75))

    return {
        "mean_estimate": float(s.mean()),
        "median_estimate": float(s.median()),
        "high_demand_threshold": high_demand_threshold,
        "proportion_high_demand": float((s >= high_demand_threshold).mean()),
        "n": len(s),
        "note": "Point estimates computed on provided data subset.",
    }


# ---------------------------------------------------------------------------
# T15 — Standard Error
# ---------------------------------------------------------------------------
def standard_error(series: pd.Series, use_cluster: bool = False,
                   cluster_col: pd.Series | None = None) -> dict:
    """
    Compute standard error of the mean (T15).

    Parameters
    ----------
    series : pd.Series  Data values.
    use_cluster : bool  If True, use day-cluster-based SE (Lemon 2003).
    cluster_col : pd.Series | None  Day identifiers for cluster SE.

    Returns
    -------
    dict with se_iid, se_cluster (if applicable), caveat.
    """
    s = series.dropna()
    n = len(s)
    std = float(s.std(ddof=1))
    se_iid = std / np.sqrt(n)

    result = {
        "n": n,
        "std": std,
        "se_iid": float(se_iid),
        "iid_caveat": (
            "IID SE assumes independent observations. "
            "Hourly bike demand has temporal autocorrelation; "
            "IID SE understates true uncertainty."
        ),
    }

    if use_cluster and cluster_col is not None:
        # Cluster-robust SE: variance of cluster-level means scaled by sqrt(n_clusters)
        aligned = pd.concat([series, cluster_col], axis=1)
        aligned.columns = ["value", "cluster"]
        cluster_means = aligned.groupby("cluster")["value"].mean()
        n_cl = len(cluster_means)
        se_cluster = float(cluster_means.std(ddof=1) / np.sqrt(n_cl))
        result["se_cluster"] = se_cluster
        result["n_clusters"] = n_cl
        result["cluster_method"] = "Mean-of-cluster-means approach"

    return result


# ---------------------------------------------------------------------------
# T16 — Bootstrap Sampling and Estimation
# ---------------------------------------------------------------------------
def bootstrap_estimate(series: pd.Series,
                       stat: str = "mean",
                       n_bootstrap: int = 2000,
                       confidence: float = 0.95,
                       seed: int = 42,
                       block_size: int | None = None) -> dict:
    """
    Bootstrap confidence interval for mean or median (T16).

    Parameters
    ----------
    stat : str  "mean" or "median".
    n_bootstrap : int  Number of bootstrap resamples.
    block_size : int | None  If provided, use block (day-block) bootstrap.
    seed : int  Random seed.
    """
    rng = np.random.default_rng(seed)
    s = series.dropna().values
    n = len(s)

    stat_func = np.mean if stat == "mean" else np.median
    observed_stat = float(stat_func(s))

    boot_stats = []
    if block_size is not None and block_size > 1:
        # Block bootstrap for temporal data
        for _ in range(n_bootstrap):
            n_blocks = max(1, n // block_size)
            starts = rng.integers(0, n - block_size + 1, size=n_blocks)
            boot_sample = np.concatenate([s[st: st + block_size] for st in starts])[:n]
            boot_stats.append(float(stat_func(boot_sample)))
        method = f"Block bootstrap (block_size={block_size})"
    else:
        # Standard resample bootstrap
        for _ in range(n_bootstrap):
            boot_sample = rng.choice(s, size=n, replace=True)
            boot_stats.append(float(stat_func(boot_sample)))
        method = "Standard resample bootstrap"

    boot_stats = np.array(boot_stats)
    alpha = 1 - confidence
    ci_lo = float(np.percentile(boot_stats, 100 * alpha / 2))
    ci_hi = float(np.percentile(boot_stats, 100 * (1 - alpha / 2)))

    return {
        "statistic": stat,
        "observed_value": observed_stat,
        "n_bootstrap": n_bootstrap,
        "confidence": confidence,
        "ci_lower": ci_lo,
        "ci_upper": ci_hi,
        "bootstrap_std": float(boot_stats.std(ddof=1)),
        "method": method,
        "boot_values": boot_stats,
    }


# ---------------------------------------------------------------------------
# T17 — Confidence Intervals (t-based)
# ---------------------------------------------------------------------------
def confidence_interval_mean(series: pd.Series,
                              confidences: list[float] | None = None) -> list[dict]:
    """
    Compute t-based confidence intervals at 90%, 95% and 99% (T17).

    Returns a list of dicts, one per confidence level.
    """
    if confidences is None:
        confidences = [0.90, 0.95, 0.99]

    s = series.dropna()
    n = len(s)
    mean = float(s.mean())
    se = float(s.std(ddof=1) / np.sqrt(n))
    df = n - 1

    results = []
    for conf in confidences:
        alpha = 1 - conf
        t_crit = scipy_stats.t.ppf(1 - alpha / 2, df=df)
        margin = t_crit * se
        results.append({
            "confidence": conf,
            "confidence_pct": f"{conf * 100:.0f}%",
            "mean": mean,
            "se": se,
            "t_critical": float(t_crit),
            "margin_of_error": float(margin),
            "ci_lower": mean - margin,
            "ci_upper": mean + margin,
            "n": n,
            "df": df,
        })
    return results


# ---------------------------------------------------------------------------
# T18 — Coverage Probability (Synthetic Simulation, clearly labeled)
# ---------------------------------------------------------------------------
def coverage_probability_simulation(
    true_mean: float = 200.0,
    true_std: float = 80.0,
    n_per_sample: int = 100,
    n_simulations: int = 2000,
    confidence: float = 0.95,
    seed: int = 42,
) -> dict:
    """
    Empirical CI coverage simulation with a known-population synthetic dataset (T18).

    SYNTHETIC SIMULATION: Does NOT use real bike demand data.
    Purpose: demonstrate that a 95% CI captures the true mean ~95% of the time.

    Parameters
    ----------
    true_mean, true_std : parameters of synthetic population.
    n_per_sample : sample size per iteration.
    n_simulations : number of independent simulations.
    """
    rng = np.random.default_rng(seed)
    captured = 0

    ci_lowers = []
    ci_uppers = []

    for _ in range(n_simulations):
        sample = rng.normal(true_mean, true_std, size=n_per_sample)
        se = sample.std(ddof=1) / np.sqrt(n_per_sample)
        t_crit = scipy_stats.t.ppf(1 - (1 - confidence) / 2, df=n_per_sample - 1)
        lo = sample.mean() - t_crit * se
        hi = sample.mean() + t_crit * se
        ci_lowers.append(lo)
        ci_uppers.append(hi)
        if lo <= true_mean <= hi:
            captured += 1

    empirical_coverage = captured / n_simulations

    return {
        "SIMULATION_TYPE": "SYNTHETIC — known-population Normal distribution",
        "true_mean": true_mean,
        "true_std": true_std,
        "n_per_sample": n_per_sample,
        "n_simulations": n_simulations,
        "nominal_confidence": confidence,
        "empirical_coverage": float(empirical_coverage),
        "captured_count": captured,
        "ci_lowers": np.array(ci_lowers),
        "ci_uppers": np.array(ci_uppers),
        "note": (
            "This is a synthetic known-population simulation to verify CI coverage. "
            "Real bike demand data is not used here."
        ),
    }


# ---------------------------------------------------------------------------
# T19 — Mean vs Median Comparison
# ---------------------------------------------------------------------------
def mean_vs_median_comparison(series: pd.Series, seed: int = 42) -> dict:
    """
    Compare mean and median as estimators under real demand and simulated skew (T19).

    Both real-data comparison and a seeded outlier/skew simulation are included.
    Simulation is clearly labelled.
    """
    rng = np.random.default_rng(seed)
    s = series.dropna()

    real_mean = float(s.mean())
    real_median = float(s.median())
    real_skew = float(s.skew())

    # Simulated skewed distribution (synthetic, clearly labeled)
    n_sim = len(s)
    lognorm_sim = rng.lognormal(mean=np.log(real_mean) if real_mean > 0 else 0,
                                sigma=1.0, size=n_sim)
    sim_mean = float(lognorm_sim.mean())
    sim_median = float(np.median(lognorm_sim))

    # Inject outliers simulation
    outlier_sim = s.values.copy().astype(float)
    outlier_idx = rng.choice(n_sim, size=max(1, n_sim // 100), replace=False)
    outlier_sim[outlier_idx] *= 5  # inject heavy outliers
    out_mean = float(outlier_sim.mean())
    out_median = float(np.median(outlier_sim))

    return {
        "real_data": {
            "mean": real_mean,
            "median": real_median,
            "skewness": real_skew,
            "mean_median_gap": abs(real_mean - real_median),
            "preferred": "median" if abs(real_skew) > 0.5 else "mean",
        },
        "synthetic_lognormal_simulation": {
            "SIMULATION_TYPE": "SYNTHETIC — lognormal for illustration",
            "mean": sim_mean,
            "median": sim_median,
            "mean_median_gap": abs(sim_mean - sim_median),
        },
        "synthetic_outlier_simulation": {
            "SIMULATION_TYPE": "SYNTHETIC — 1% extreme outliers injected",
            "mean": out_mean,
            "median": out_median,
            "outlier_impact_on_mean": abs(out_mean - real_mean),
            "outlier_impact_on_median": abs(out_median - real_median),
        },
        "interpretation": (
            "Median is more robust to outliers and skewness. "
            "For planning purposes, the median demand gives a more conservative and "
            "reliable planning target than the mean."
        ),
    }
