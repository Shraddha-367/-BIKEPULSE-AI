"""
T10 + T11 + T12 + T13 — Random Sampling, Population/Sample Stats,
Sampling Distribution, Central Limit Theorem
=================================================================
All sampling uses reproducible seeds. Temporal-dependence caveats
are documented; no iid claims are made for hourly bike data.
"""

import logging
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# T10 — Four Sampling Schemes
# ---------------------------------------------------------------------------
def simple_random_sample(df: pd.DataFrame, n: int = 500,
                         seed: int = 42) -> pd.DataFrame:
    """
    Simple random sample (without replacement) from full dataset (T10).
    NOTE: Ignores temporal structure; used for illustration only.
    """
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(df), size=min(n, len(df)), replace=False)
    sample = df.iloc[sorted(indices)].copy()
    sample.attrs["sampling_scheme"] = "simple_random"
    sample.attrs["sample_n"] = len(sample)
    return sample


def systematic_sample(df: pd.DataFrame, k: int | None = None,
                      n_desired: int = 500) -> pd.DataFrame:
    """
    Systematic sampling: select every k-th record (T10).
    k is computed to yield approximately n_desired records.
    """
    if k is None:
        k = max(1, len(df) // n_desired)
    sample = df.iloc[::k].copy()
    sample.attrs["sampling_scheme"] = "systematic"
    sample.attrs["step_k"] = k
    sample.attrs["sample_n"] = len(sample)
    return sample


def stratified_sample(df: pd.DataFrame, strat_col: str = "season",
                      n_per_stratum: int = 125,
                      seed: int = 42) -> pd.DataFrame:
    """
    Proportional stratified sampling by season (T10).
    n_per_stratum rows sampled from each stratum.
    """
    rng = np.random.default_rng(seed)
    strata = []
    for _, group in df.groupby(strat_col):
        n = min(n_per_stratum, len(group))
        sampled = group.sample(n=n, random_state=int(rng.integers(0, 10000)))
        strata.append(sampled)
    sample = pd.concat(strata).sort_index()
    sample.attrs["sampling_scheme"] = "stratified"
    sample.attrs["strat_col"] = strat_col
    sample.attrs["sample_n"] = len(sample)
    return sample


def cluster_sample(df: pd.DataFrame, cluster_col: str = "dteday",
                   n_clusters: int = 30,
                   seed: int = 42) -> pd.DataFrame:
    """
    Cluster sampling: randomly select n_clusters days, include all hours (T10).
    This is more appropriate for temporal data than simple random sampling.
    """
    rng = np.random.default_rng(seed)
    # Ensure dteday is date-only for grouping
    if "dteday" not in df.columns:
        raise ValueError("Column 'dteday' required for cluster sampling.")
    unique_days = df["dteday"].dt.date.unique()
    selected_days = rng.choice(unique_days, size=min(n_clusters, len(unique_days)),
                               replace=False)
    mask = df["dteday"].dt.date.isin(selected_days)
    sample = df[mask].copy()
    sample.attrs["sampling_scheme"] = "cluster"
    sample.attrs["n_clusters"] = n_clusters
    sample.attrs["sample_n"] = len(sample)
    return sample


def get_all_samples(df: pd.DataFrame, seed: int = 42) -> dict[str, pd.DataFrame]:
    """Return all four sampling schemes."""
    return {
        "simple_random": simple_random_sample(df, n=500, seed=seed),
        "systematic": systematic_sample(df, n_desired=500),
        "stratified": stratified_sample(df, seed=seed),
        "cluster": cluster_sample(df, n_clusters=30, seed=seed),
    }


# ---------------------------------------------------------------------------
# T11 — Population vs Sample Statistics
# ---------------------------------------------------------------------------
def population_vs_sample_stats(df: pd.DataFrame,
                                sample: pd.DataFrame,
                                col: str = "cnt") -> dict:
    """
    Side-by-side population and sample statistics (T11).

    Parameters
    ----------
    df : pd.DataFrame   Full (population) dataset.
    sample : pd.DataFrame  Sample subset.
    col : str  Numeric column to compare.

    Returns
    -------
    dict
        Population stats, sample stats, and comparison.
    """
    pop = df[col].dropna()
    samp = sample[col].dropna()

    def _stats(s):
        q1, q3 = np.percentile(s, [25, 75])
        return {
            "n": len(s),
            "mean": round(float(s.mean()), 4),
            "median": round(float(s.median()), 4),
            "std": round(float(s.std(ddof=1)), 4),
            "variance": round(float(s.var(ddof=1)), 4),
            "q1": round(float(q1), 4),
            "q3": round(float(q3), 4),
            "iqr": round(float(q3 - q1), 4),
        }

    pop_stats = _stats(pop)
    samp_stats = _stats(samp)
    return {
        "population": pop_stats,
        "sample": samp_stats,
        "sampling_scheme": sample.attrs.get("sampling_scheme", "unknown"),
        "mean_bias": round(samp_stats["mean"] - pop_stats["mean"], 4),
    }


# ---------------------------------------------------------------------------
# T12 — Sampling Distribution
# ---------------------------------------------------------------------------
def sampling_distribution(df: pd.DataFrame, col: str = "cnt",
                           n_samples: int = 1000,
                           sample_size: int = 100,
                           seed: int = 42) -> dict:
    """
    Repeatedly draw samples of size sample_size and record means (T12).

    NOTE: Ignores temporal autocorrelation for illustration.
    See caveat in returned dict.
    """
    rng = np.random.default_rng(seed)
    data = df[col].dropna().values
    means = []
    for _ in range(n_samples):
        idx = rng.choice(len(data), size=sample_size, replace=False)
        means.append(float(data[idx].mean()))

    means_arr = np.array(means)
    return {
        "sample_size": sample_size,
        "n_iterations": n_samples,
        "sampling_means": means_arr,
        "mean_of_means": float(means_arr.mean()),
        "std_of_means": float(means_arr.std(ddof=1)),
        "theoretical_se": float(np.std(data, ddof=1) / np.sqrt(sample_size)),
        "caveat": (
            "Bike rental data has temporal autocorrelation. "
            "Standard SRS SE underestimates true variability. "
            "Day-block bootstrap gives more realistic standard errors."
        ),
    }


# ---------------------------------------------------------------------------
# T13 — Central Limit Theorem
# ---------------------------------------------------------------------------
def central_limit_theorem(df: pd.DataFrame, col: str = "cnt",
                          sample_sizes: list[int] | None = None,
                          n_iterations: int = 1000,
                          seed: int = 42) -> dict:
    """
    Demonstrate CLT across different sample sizes (T13).

    Shows that sample-mean distributions approach Normal as n increases,
    with explicit caveats about temporal dependence.

    Parameters
    ----------
    sample_sizes : list[int]   Default: [30, 50, 100, 200].
    """
    if sample_sizes is None:
        sample_sizes = [30, 50, 100, 200]

    rng = np.random.default_rng(seed)
    data = df[col].dropna().values
    population_std = float(np.std(data, ddof=1))

    results = {}
    for n in sample_sizes:
        means = np.array([
            data[rng.choice(len(data), size=n, replace=False)].mean()
            for _ in range(n_iterations)
        ])
        sw_stat, sw_p = scipy_stats.shapiro(means[:5000])
        results[n] = {
            "sample_size": n,
            "mean_of_means": float(means.mean()),
            "std_of_means": float(means.std(ddof=1)),
            "theoretical_se": population_std / np.sqrt(n),
            "shapiro_stat": float(sw_stat),
            "shapiro_p": float(sw_p),
            "is_normal_p05": bool(sw_p > 0.05),
            "sample_means": means,
        }

    return {
        "sample_sizes": sample_sizes,
        "results": results,
        "population_mean": float(data.mean()),
        "population_std": population_std,
        "n_iterations": n_iterations,
        "clt_caveat": (
            "The CLT assumes iid observations. Hourly bike counts exhibit "
            "strong temporal autocorrelation (morning/evening peaks, seasonal cycles). "
            "Larger samples do converge to approximately Normal sample-mean distributions, "
            "but SE estimates may be optimistic. Day-block bootstrap is preferred "
            "for inference on this type of data."
        ),
    }
